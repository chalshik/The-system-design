## High Level Architecture

### 1. Event Collection
I distinguished event producers: system events, transactional, periodic, and external systems. They communicate only with the Producer service, which enqueues events into the first queue. These messages are pulled by the Notification Service. By adding a queue layer between the Notification Service and producers, we ensure fault tolerance. This part explains how we collect different events that need to be delivered.

### 2. Event Processing
The Notification Service sets configuration, templates, and checks user preferences. I added a cache layer to store user preferences and already-sent message IDs to avoid duplication. To avoid a single point of failure, I used a clustered Redis. The second part is routing events to correct channels — for this we use a second queue with channel-specific topics. I used RabbitMQ due to its simplicity, and because we don't need persistence of already-sent messages.

### 3. Delivery
We have clustered channel workers for email, in-app, and push. They pull data from their specific topics and deliver messages via channel-specific providers. In case of failure, messages are routed to the DLQ — a built-in RabbitMQ feature for redelivery.

---

## Trade-offs

### 1. Two-Queue Architecture (RabbitMQ)
I used RabbitMQ to make the Notification Service and channel workers fault tolerant. During event gathering and processing, data could be lost — two queues address this: the first collects events, the second routes messages to channels. The trade-off is additional latency due to extra layers. Both queues are fault tolerant via RabbitMQ distributed clustering.

### 2. Redis for Preferences
The requirements specify respecting user preferences, meaning we must look up preferences for every event. This adds load on the database. Since preferences change rarely, we cache them in Redis. To ensure fault tolerance, we use a clustered Redis setup.

### 3. Cassandra as Primary Database
We have a high volume of writes and updates — after notification persistence, their status changes frequently. Read volume is also high for in-app notifications and retry logic. Cassandra offers distributed equal nodes by default, making it highly available. It is also easier to shard compared to SQL-based databases, which have significant complexity at scale.

---

## Data Models

### Notifications Collection

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique identifier |
| user_id | UUID | Reference to user |
| type | ENUM | email, push, inapp |
| title | TEXT | Notification title |
| body | TEXT | Notification body |
| attachments | LIST\<TEXT\> | URLs to attachments |
| status | ENUM | pending, sent, failed |
| is_read | BOOLEAN | Only relevant for inapp |
| created_at | TIMESTAMP | Creation time |

**Indexes:**
- `(user_id, created_at)` — fetch user notifications sorted by time
- `(status)` — retry jobs fetch failed notifications

---

### Device Tokens Collection

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique identifier |
| user_id | UUID | Reference to user |
| token | TEXT | Device push token |
| platform | ENUM | ios, android |
| created_at | TIMESTAMP | Token registration time |

**Indexes:**
- `(user_id)` — fetch all tokens for a user (one user, multiple devices)

---

### Preferences Collection

| Field | Type | Description |
|---|---|---|
| user_id | UUID | Reference to user |
| email_enabled | BOOLEAN | Email notifications on/off |
| push_enabled | BOOLEAN | Push notifications on/off |
| inapp_enabled | BOOLEAN | In-app notifications on/off |
| created_at | TIMESTAMP | Creation time |

**Indexes:**
- `(user_id)` — lookup preferences per user

---

### Users Collection

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique identifier |
| email | TEXT | Email address for delivery |
| phone | TEXT | Phone number (optional) |
| created_at | TIMESTAMP | Creation time |

**Indexes:**
- `(email)` — lookup user by email