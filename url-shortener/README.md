### System Design: High-Scale URL Shortener

This architecture is built for **high availability**, **massive storage**, and **zero-collision** performance. Here is the breakdown of the design:

---
### 1. ID Generation & Encoding (The Core)
To ensure every short URL is unique, the system avoids risky hashing. Instead, it uses a **distributed counter service**.

* **The Range Handler:** A separate service assigns unique "blocks" of numbers (ranges) to different application workers. This prevents **race conditions** because no two workers ever hold the same set of numbers.
* **Collision-Free:** Since every URL gets a unique incrementing ID, there is zero chance of a collision.
* **Base32 Encoding:** The unique integer ID is converted into **Base32**. This keeps the URL short and human-readable while using a safe character set (A-Z, 2-7) that avoids ambiguous characters.

---

### 2. Fast Lookup Layer (Redis)
Because URL shorteners are "read-heavy" (links are clicked more than they are created), a **Redis** cache sits in front of the database.

* **Speed:** Redis stores active mappings in-memory, allowing for microsecond redirection.
* **Database Protection:** By checking the cache first, we prevent the primary database from being overwhelmed by traffic spikes for viral links.

---

### 3. Scalable Storage (Apache Cassandra)
For the permanent storage of billions of URL mappings, **Apache Cassandra** was chosen over traditional SQL.

* **High Availability:** Cassandra’s masterless design ensures that the service stays online even if individual hardware nodes fail.
* **Massive Scale:** It is optimized for high-volume writes and can scale horizontally simply by adding more nodes as the data grows.
* **Performance:** It allows the system to store a nearly infinite amount of URL data without a drop in lookup performance.



---

### Summary of Data Flow
1.  **Shortening:** User provides a URL $\to$ Worker gets a unique ID $\to$ Encodes to Base32 $\to$ Saves to Cassandra and Redis.
2.  **Redirection:** User clicks link $\to$ System checks **Redis** (Hit) $\to$ If Miss, query **Cassandra** $\to$ Update Redis $\to$ Redirect user.