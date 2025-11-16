import pika
import json
import time
import os
from sqlmodel import Session
from ..tracker.models import RequestLog
from ..tracker.schemas import RequestTrackingMessage
from ..tracker.services import create_request_log
from ..geo.ip_geolocation import get_getlocation
from ..db.database import get_session

class RabbitMQConsumer:
    def __init__(self):
        self.rabbitmq_url=os.getenv("RABBITMQ_URL")
        self.queue_name=os.getenv("RABBITMQ_QUEUE_NAME")
        self.exchange_name=os.getenv("RABBITMQ_EXCHANGE_NAME")
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
                    durable=True
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

                # set prefetch count
                self.channel.basic_qos(prefetch_count=10)

                print("✅ Connected to RabbitMQ")
                return True

            except Exception as e:
                retries+=1
                print(f"❌ Failed to connect to RabbitMQ (attempt {retries}/{self.max_retries}): {e}")
                time.sleep(5)
        
        raise Exception(f"❌ Failed to connect to RabbitMQ after {self.max_retries} attempts")

    def process_message(self,ch,method,props,body):
        retries=0
        try:
            message_data=json.loads(body)
            message=RequestTrackingMessage(**message_data)

            geo_data=get_getlocation(message.client_ip) if message.client_ip else {
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
                    print(f"✅ Successfully processed: {message.method} {message.path} - {message.status_code}")
                    db_session.close()
                    return
                except Exception as db_error:
                    retries+=1
                    print(f"⚠️ Database error (attempt {retries}/{self.max_retries}): {db_error}")
                    if db_session:
                        db_session.close()
                    
                    if retries < self.max_retries:
                        time.sleep(2 ** retries)  # Exponential backoff
                    else:
                        # Send to DLQ after max retries
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        print(f"❌ Message sent to DLQ after {self.max_retries} failed attempts")

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

    def start_consuming(self):
        try:
            print("✅ Starting to consume messages from RabbitMQ")
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.process_message,
                auto_ack=False
            )
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("❌ Keyboard interrupt detected. Shutting down...")
            self.stop()
        except Exception as e:
            print(f"❌ Error starting consumer: {e}")
            raise

    def stop(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("✅ RabbitMQ Connection closed")