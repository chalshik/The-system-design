### System Design: High-Scale URL Shortener

This architecture is built for **high availability**, **massive storage**, and **zero-collision** performance. It uses a modular design where high-level storage concepts are demonstrated via local abstraction.

---

### 1. ID Generation & Encoding (The Core)
To ensure every short URL is unique, the system avoids risky hashing algorithms that can clash. Instead, it uses a **distributed counter service**.

* **The Range Handler:** A separate service assigns unique "blocks" of numbers (ranges) to different application workers. This prevents **race conditions** because no two workers ever hold the same set of numbers at the same time.
* **Collision-Free:** Since every URL is assigned a unique incrementing integer, there is zero chance of a collision.
* **Base32 Encoding:** This integer is converted into a **Base32** string. This keeps the URL short and human-readable while using a safe character set (A-Z, 2-7) that avoids ambiguous characters like "0" and "O".



---

### 2. Fast Lookup Layer (Redis)
Because URL shorteners are "read-heavy" (links are clicked thousands of times more than they are created), a **Redis** cache sits in front of the persistent storage.

* **Look-aside Cache:** The system checks Redis first. If the mapping exists, it redirects in microseconds.
* **Database Protection:** By checking the cache first, we shield the primary database from being overwhelmed by traffic spikes, such as viral links or bot activity.



---

### 3. Scalable Storage (Cassandra via SQLite Abstraction)
The architecture is designed to eventually live on **Apache Cassandra** to handle billions of mappings across multiple data centers.

* **The Design Choice:** Cassandra was selected for its masterless architecture and horizontal scalability, ensuring the system never has a single point of failure.
* **Implementation Abstraction:** In the current code implementation, **SQLite** is used as an abstraction layer. This simulates the persistent storage and unique indexing requirements of a production database while remaining lightweight and portable for demonstration.



---

### Summary of Data Flow
1.  **Shortening:** User provides a URL $\to$ Worker gets unique ID $\to$ Encodes to Base32 $\to$ Saves to SQLite (Persistent Storage) and Redis (Cache).
2.  **Redirection:** User clicks link $\to$ System checks **Redis** (Hit) $\to$ If Miss, query **SQLite** $\to$ Update Redis $\to$ Redirect user.