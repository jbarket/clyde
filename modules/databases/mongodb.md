# MongoDB Guidelines

## Document Design

### Schema Design Patterns
- Design documents based on query patterns
- Embed related data when accessed together
- Reference when data is large or frequently updated
- Use consistent field naming conventions

```javascript
// Good: Embedded design for blog posts
{
  _id: ObjectId("..."),
  title: "Blog Post Title",
  content: "Post content...",
  author: {
    name: "John Doe",
    email: "john@example.com"
  },
  tags: ["tech", "programming"],
  comments: [
    {
      author: "Jane",
      text: "Great post!",
      date: ISODate("2024-01-01")
    }
  ],
  createdAt: ISODate("2024-01-01"),
  updatedAt: ISODate("2024-01-01")
}
```

## Query Optimization

### Indexing Strategy
```javascript
// Create compound indexes for common queries
db.users.createIndex({ "email": 1 })
db.posts.createIndex({ "author.email": 1, "createdAt": -1 })
db.posts.createIndex({ "tags": 1, "published": 1 })
```

### Aggregation Pipelines
```javascript
// Use aggregation for complex queries
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: {
      _id: "$customerId",
      totalSpent: { $sum: "$amount" },
      orderCount: { $sum: 1 }
    }
  },
  { $sort: { totalSpent: -1 } }
])
```