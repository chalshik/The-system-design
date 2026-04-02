

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