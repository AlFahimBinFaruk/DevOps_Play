import pika
import json
import time
import os
from ..tracker.schemas import RequestTrackingMessage
from ..tracker.services import create_request_log
from ..geo.ip_geolocation import get_geolocation
from ..db.database import get_session
import logging

logger=logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.rabbitmq_url=os.getenv("RABBITMQ_URL")
        self.queue_name=os.getenv("RABBITMQ_QUEUE")
        self.exchange_name=os.getenv("RABBITMQ_EXCHANGE")
        self.connection=None
        self.channel=None
        self.max_retries=3

    def connect(self):
        retries=0
        while retries<self.max_retries:
            try:
                parameters=pika.URLParameters(self.rabbitmq_url)
                self.connection=pika.BlockingConnection(parameters)
                self.channel=self.connection.channel()

                # Declare Exchange
                self.channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type="fanout",
                    durable=True # durable means the exchange will not be deleted when the RabbitMQ server is restarted.
                )
                # Declare queue
                self.channel.queue_declare(
                    queue=self.queue_name,
                    durable=True,
                    arguments={
                        "x-dead-letter-exchange":f"{self.exchange_name}_dlx"
                    }
                )
                # Bind Queue to Exchange
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=self.queue_name
                )

                """
                Declare dead letter exchange and queue.
                """
                self.channel.exchange_declare(
                    exchange=f"{self.exchange_name}_dlx",
                    exchange_type="fanout",
                    durable=True
                )
                self.channel.queue_declare(
                    queue=f"{self.queue_name}_dlq",
                    durable=True,
                    arguments={
                        "x-dead-letter-exchange":self.exchange_name
                    }
                )
                self.channel.queue_bind(
                    exchange=f"{self.exchange_name}_dlx",
                    queue=f"{self.queue_name}_dlq"
                )

                # rabbitmq will send 10 messages to the consumer at a time.
                # won't send the 11th message until the consumer acknowledges the one of theprevious 10 message.
                self.channel.basic_qos(prefetch_count=10)

                logger.info("✅ Connected to RabbitMQ")
                return True

            except Exception as e:
                retries+=1
                logger.error(f"❌ Failed to connect to RabbitMQ (attempt {retries}/{self.max_retries}): {e}")
                time.sleep(5)
        
        raise Exception(f"❌ Failed to connect to RabbitMQ after {self.max_retries} attempts")

    def process_message(self,ch,method,props,body):
        retries=0
        try:
            message_data=json.loads(body)
            message=RequestTrackingMessage(**message_data)

            geo_data=get_geolocation(message.client_ip) if message.client_ip else {
                "country": None,
                "city": None,
                "latitude": None,
                "longitude": None
            }

            while retries<self.max_retries:
                try:
                    db_session=next(get_session())
                    request_log=create_request_log(db_session,message,geo_data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"✅ Successfully processed: {message.method} {message.path} - {message.status_code}")
                    db_session.close()
                    return
                except Exception as db_error:
                    retries+=1
                    logger.error(f"⚠️ Database error (attempt {retries}/{self.max_retries}): {db_error}")
                    if db_session:
                        db_session.close()
                    
                    if retries < self.max_retries:
                        time.sleep(2 ** retries)  # Exponential backoff
                    else:
                        # Send to DLQ after max retries
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        logger.error(f"❌ Message sent to DLQ after {self.max_retries} failed attempts")

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

    def start_consuming(self):
        try:
            logger.info("✅ Starting to consume messages from RabbitMQ")
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.process_message,
                auto_ack=False
            )
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.error("❌ Keyboard interrupt detected. Shutting down...")
            self.stop()
        except Exception as e:
            logger.error(f"❌ Error starting consumer: {e}")
            raise

    def stop(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("✅ RabbitMQ Connection closed")