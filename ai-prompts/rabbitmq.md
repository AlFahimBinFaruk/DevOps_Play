# Feature: Request Tracking with RabbitMQ

## Architecture
1. **Publishers:** note-management, user-management (via middleware)
2. **Message Broker:** RabbitMQ (separate Docker container)
3. **Consumer:** request-tracking service (new service in FastAPI)
4. **Database:** PostgreSQL (start simple) or ClickHouse (if high volume expected)
5. User ip-api.com if needed.

## Data Captured
- Timestamp, service, method, path, query_params
- Client IP (anonymized), user_agent, referer, origin
- Geolocation: country, city, lat/long (from IP via MaxMind)
- User context: user_id (if authenticated)
- Response: status_code, duration_ms

## Data NOT Captured (Privacy)
- Request/response bodies
- Authorization headers
- Sensitive query parameters

## Services Structure
services/
├── user-management/       # Existing - add RabbitMQ publisher
├── note-management/       # Existing - add RabbitMQ publisher  
└── request-tracking/      # NEW - RabbitMQ consumer + DB writer
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    └── src/
        ├── main.py
        ├── consumer/
        │   └── rabbitmq_consumer.py
        ├── db/
        │   └── database.py
        ├── geo/
        │   └── ip_geolocation.py
        └── models/
            └── schemas.py

## RabbitMQ Configuration
- Exchange: "request_tracking" (fanout or topic)
- Queue: "request_tracking_queue" (durable)
- Messages: Persistent
- Acknowledgment: Manual (after successful DB write)
- Dead Letter Exchange: For failed messages
- Prefetch: 10 messages per consumer

## Failure Handling
- Publisher: Fire-and-forget with try/except (don't block API)
- Consumer: Manual ACK only after DB write succeeds
- Retry: 3 attempts with exponential backoff
- DLQ: Failed messages go to dead letter queue for investigation

## Privacy & Compliance
- Anonymize IP addresses (last octet)
- Retention: 90 days, then auto-delete
- No sensitive data (passwords, tokens, PII)
- Add to privacy policy

## Performance
- Exclude paths: /health, /metrics, /ready
- Optional sampling: 100% errors, 10% success (if high traffic)
- Multiple consumer instances for parallel processing