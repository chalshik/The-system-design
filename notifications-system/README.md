Explanation of my high level architecture,so 
1) I distiungished event producers like system events, transactional, periodic and external systems. They talk only to producer service which enqueues first queue for all possible events that must be delivered, this messages soonly will be pulled by notifications service, by adding queue layer between notification service and producer we ensure it is fault tolerant. This part explains how we collect different events that needs to be delivered 
2) Second part is processing this events, notification services sets configuration, templates, checks preferences of users, so I added cache layer where we store preferences for users and information about sent messages already to avoid duplicaton, to avoid single point of failure I used clustered redis. And second part is routing this events to correct channels, for this we use second queue with channel topics. For queue I used rabbitmq, due to simplicity and we dont need persistence of sent messages. 
3) Delivering part we have clustered channel workers, there are : email, in-app, push. They will pull data from specific topics and using their specific interface providers, send their messages. In case of failure we failure it will be navigated to DLQ rabbitmq built in feature to resend messages.



## Notifications Collection

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique identifier |
| user_id | UUID | Reference to user |
| type | ENUM | email, push, inapp |
| title | TEXT | Notification title |
| body | TEXT | Notification body |
| attachments | LIST<TEXT> | URLs to attachments |
| status | ENUM | pending, sent, failed |
| is_read | BOOLEAN | Only relevant for inapp |
| created_at | TIMESTAMP | Creation time |

**Indexes:**
- (user_id, created_at) — fetch user notifications sorted by time
- (status) — retry jobs fetch failed notifications
## Device Tokens Collection

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique identifier |
| user_id | UUID | Reference to user |
| token | TEXT | Device push token |
| platform | ENUM | ios, android |
| created_at | TIMESTAMP | Token registration time |

**Indexes:**
- user_id — fetch all tokens for a user (one user, multiple devices)
## Preferences Collection

| Field | Type | Description |
|---|---|---|
| user_id | UUID | Reference to user |
| email_enabled | BOOLEAN | Email notifications on/off |
| push_enabled | BOOLEAN | Push notifications on/off |
| inapp_enabled | BOOLEAN | In-app notifications on/off |
| created_at | TIMESTAMP | Creation time |

**Indexes:**
- (user_id) — lookup preferences per user

---

## Users Collection

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique identifier |
| email | TEXT | Email address for delivery |
| phone | TEXT | Phone number (optional) |
| created_at | TIMESTAMP | Creation time |

**Indexes:**
- (email) — lookup user by email