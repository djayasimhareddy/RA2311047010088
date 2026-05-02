# Notification System Design

## Stage 1: API Design

### Create Notification

POST /notifications
Request:
{
"studentId": "string",
"type": "Event | Result | Placement",
"message": "string"
}

Response:
{
"id": "uuid",
"status": "created"
}

---

### Get Notifications

GET /notifications?studentId={id}&page=1&limit=20

Response:
{
"notifications": [],
"total": 100
}

---

### Mark as Read

PUT /notifications/{id}/read

Response:
{
"status": "updated"
}

---

### Delete Notification

DELETE /notifications/{id}

---

### Real-Time Delivery

Use WebSockets or Server-Sent Events to push notifications instantly to clients.

---

## Stage 2: Database Design

Database: PostgreSQL

Table: notifications

* id (UUID, Primary Key)
* studentId (Indexed)
* type (ENUM: Event, Result, Placement)
* message (TEXT)
* isRead (BOOLEAN, default false)
* createdAt (TIMESTAMP, Indexed)

Indexes:

* (studentId, isRead, createdAt DESC)

Scaling Strategy:

* Table partitioning by date
* Read replicas for high traffic

---

## Stage 3: Query Optimization

Original Query:
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;

Problem:

* Full table scan without index
* Slow sorting on large data

Optimized:
CREATE INDEX idx_student_read_created
ON notifications(studentID, isRead, createdAt DESC);

Use pagination:
LIMIT 20 OFFSET 0;

---

## Stage 4: Performance Optimization

* Use Redis caching for unread notifications
* Implement pagination (avoid loading all data)
* Lazy loading on UI
* Use CDN for static assets
* Batch DB reads

Tradeoffs:

* Cache adds complexity but reduces DB load
* Pagination improves speed but needs state handling

---

## Stage 5: Reliability & Scalability

Problems in naive system:

* Sequential processing
* No retry on failure
* Blocking operations

Solution:

* Use message queue (Kafka / RabbitMQ)
* Asynchronous workers
* Retry mechanism with exponential backoff
* Idempotent operations

Improved Flow:

1. Save notification to DB
2. Push event to queue
3. Worker sends email/app notification
4. Retry if failed

---

## Stage 6: Priority Inbox

Goal:
Show top N important unread notifications

Priority Calculation:
Priority Score = Weight + Recency

Weights:

* Placement = 3
* Result = 2
* Event = 1

Recency:

* Recent notifications get higher score

Implementation:

* Use Min Heap (Priority Queue)
* Maintain top N (10/15/20)

Efficient Strategy:

* Insert new notifications into heap
* Remove lowest priority when size exceeds N

Result:
Fast retrieval of most important notifications
