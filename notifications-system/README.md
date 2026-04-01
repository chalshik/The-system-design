Beginning of journey 

API Design: 
GET notifications/ 
POST notifications/push 

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