## Querying NoSQL Databases

Querying NoSQL databases requires a different approach compared to relational databases due to their diverse data models and storage mechanisms. This guide focuses on MongoDB, a popular NoSQL database, and explores how to query data effectively using its powerful query language.

### Introduction to MongoDB

#### Data Model

- MongoDB stores data in **documents**, which are JSON-like objects capable of containing nested documents and arrays.
- Each document is stored within a **collection**, analogous to a table in relational databases.
- The document model allows for complex data structures and offers **flexibility** in schema design.

**Example Document:**

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "John Doe",
  "age": 30,
  "email": "john.doe@example.com",
  "addresses": [
    {
      "street": "123 Main St",
      "city": "Anytown",
      "zip": "12345"
    },
    {
      "street": "456 Elm St",
      "city": "Othertown",
      "zip": "67890"
    }
  ]
}
```

#### Query Language

- MongoDB uses a JSON-like syntax for queries, making it intuitive for developers familiar with **JSON**.
- The query language provides a rich set of **operators** for filtering, projection, sorting, and aggregation.

**Examples of Query Operators:**

- `$eq`, `$ne`: Equal, Not Equal
- `$gt`, `$gte`, `$lt`, `$lte`: Greater Than, Greater Than or Equal, Less Than, Less Than or Equal
- `$in`, `$nin`: In, Not In
- `$and`, `$or`, `$not`, `$nor`: Logical Operators

### Basic Queries

#### Find

- The `find` method retrieves documents from a collection that match specified **filter** criteria.
- The syntax for `find` is `db.collection.find(query, projection)`, where `query` specifies selection criteria and `projection` determines the fields to include or exclude.

**Example: Retrieve all users aged 25**

**Sample Data in `users` Collection:**

Suppose we have the following documents in our `users` collection:

```javascript
db.users.insertMany([
  { _id: 1, name: "Alice", age: 25, email: "alice@example.com", city: "New York" },
  { _id: 2, name: "Bob", age: 30, email: "bob@example.com", city: "Los Angeles" },
  { _id: 3, name: "Carol", age: 25, email: "carol@example.com", city: "Chicago" },
  { _id: 4, name: "Dave", age: 28, email: "dave@example.com", city: "New York" }
])
```

**Code:**

```javascript
db.users.find({ age: 25 })
```

**Result:**

```javascript
{ "_id" : 1, "name" : "Alice", "age" : 25, "email" : "alice@example.com", "city" : "New York" }
{ "_id" : 3, "name" : "Carol", "age" : 25, "email" : "carol@example.com", "city" : "Chicago" }
```

**Example with Projection: Retrieve users aged 25, but only show their names and emails**

**Code:**

```javascript
db.users.find(
  { age: 25 },
  { name: 1, email: 1, _id: 0 }
)
```

**Result:**

```javascript
{ "name" : "Alice", "email" : "alice@example.com" }
{ "name" : "Carol", "email" : "carol@example.com" }
```

#### Count

- The `count` method returns the **number** of documents that match a query.
- The syntax for `count` is `db.collection.countDocuments(query)`.

**Example: Count the number of users aged 25**

**Code:**

```javascript
db.users.countDocuments({ age: 25 })
```

**Result:**

```
2
```

#### Distinct

- The `distinct` method finds the unique **values** for a specified field across a collection.
- The syntax for `distinct` is `db.collection.distinct(field, query)`.

**Example: Get a list of unique cities where users aged 25 live**

**Code:**

```javascript
db.users.distinct("city", { age: 25 })
```

**Result:**

```javascript
[ "New York", "Chicago" ]
```

### Advanced Queries

#### Aggregation

- Aggregation operations process data records and return **computed** results.
- MongoDB's aggregation framework provides an efficient way to perform data analysis using a pipeline of stages.

**Syntax:**

```javascript
db.collection.aggregate(pipeline, options)
```

- The `pipeline` is an array of stages that process and transform the data.

**Example: Group users by city and count the number of users in each city**

**Sample Data:**

Using the same `users` collection as before.

**Code:**

```javascript
db.users.aggregate([
  { $group: { _id: "$city", count: { $sum: 1 } } }
])
```

**Result:**

```javascript
{ "_id" : "New York", "count" : 2 }
{ "_id" : "Los Angeles", "count" : 1 }
{ "_id" : "Chicago", "count" : 1 }
```

- The `$group` stage groups documents by the specified `_id` expression.
- The `$sum: 1` increments the count by 1 for each document in the group.

**Example: Calculate the average age of users in each city**

**Code:**

```javascript
db.users.aggregate([
  { $group: { _id: "$city", averageAge: { $avg: "$age" } } }
])
```

**Result:**

```javascript
{ "_id" : "New York", "averageAge" : 26.5 }
{ "_id" : "Los Angeles", "averageAge" : 30 }
{ "_id" : "Chicago", "averageAge" : 25 }
```

#### Text Search

MongoDB supports text search through **text indexes**, allowing you to perform search operations on string content.

**Sample Data in `articles` Collection:**

```javascript
db.articles.insertMany([
  { _id: 1, title: "Introduction to MongoDB", content: "MongoDB is a NoSQL database." },
  { _id: 2, title: "NoSQL Databases", content: "NoSQL databases are non-relational." },
  { _id: 3, title: "Relational Databases", content: "SQL databases are relational." },
  { _id: 4, title: "Advantages of NoSQL", content: "NoSQL databases like MongoDB are scalable." }
])
```

**Creating a Text Index:**

```javascript
db.articles.createIndex({ content: "text" })
```

The syntax for text search is `db.collection.find({ $text: { $search: searchString } })`.

**Example: Find articles that contain the word "NoSQL"**

**Code:**

```javascript
db.articles.find({ $text: { $search: "NoSQL" } })
```

**Result:**

```javascript
{ "_id" : 1, "title" : "Introduction to MongoDB", "content" : "MongoDB is a NoSQL database." }
{ "_id" : 2, "title" : "NoSQL Databases", "content" : "NoSQL databases are non-relational." }
{ "_id" : 4, "title" : "Advantages of NoSQL", "content" : "NoSQL databases like MongoDB are scalable." }
```

**Advanced Text Search:**

For **phrase** search, enclose the phrase in double quotes.

**Example: Find articles containing the phrase "NoSQL databases"**

**Code:**

```javascript
db.articles.find({ $text: { $search: "\"NoSQL databases\"" } })
```

**Result:**

```javascript
{ "_id" : 2, "title" : "NoSQL Databases", "content" : "NoSQL databases are non-relational." }
{ "_id" : 4, "title" : "Advantages of NoSQL", "content" : "NoSQL databases like MongoDB are scalable." }
```

To **exclude** terms, use a minus sign before the word.

**Example: Find articles that contain "NoSQL" but not "MongoDB"**

**Code:**

```javascript
db.articles.find({ $text: { $search: "NoSQL -MongoDB" } })
```

**Result:**

```javascript
{ "_id" : 2, "title" : "NoSQL Databases", "content" : "NoSQL databases are non-relational." }
```

#### Geospatial Queries

- MongoDB provides powerful geospatial indexing and querying capabilities for **location-based** data.

**Storing Location Data:**

**Sample Data in `places` Collection:**

```javascript
db.places.insertMany([
  {
    _id: 1,
    name: "Central Park",
    location: {
      type: "Point",
      coordinates: [-73.9667, 40.78]
    }
  },
  {
    _id: 2,
    name: "Times Square",
    location: {
      type: "Point",
      coordinates: [-73.9855, 40.7580]
    }
  },
  {
    _id: 3,
    name: "Empire State Building",
    location: {
      type: "Point",
      coordinates: [-73.9857, 40.7484]
    }
  }
])
```

**Creating a 2dsphere Index:**

```javascript
db.places.createIndex({ location: "2dsphere" })
```

The syntax for geospatial queries is:

```javascript
db.collection.find({
  location: {
    $near: {
      $geometry: point,
      $maxDistance: distance
    }
  }
})
```

**Example: Find places within 1,000 meters of Times Square**

**Code:**

```javascript
db.places.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.9855, 40.7580]
      },
      $maxDistance: 1000  // distance in meters
    }
  }
})
```

**Result:**

Assuming that the Empire State Building is within 1,000 meters of Times Square:

```javascript
{ "_id" : 2, "name" : "Times Square", "location" : { "type" : "Point", "coordinates" : [ -73.9855, 40.758 ] } }
{ "_id" : 3, "name" : "Empire State Building", "location" : { "type" : "Point", "coordinates" : [ -73.9857, 40.7484 ] } }
```

- The `$near` operator finds documents near a specified **point**.
- The `$geometry` field defines the point with coordinates.
- The `$maxDistance` sets the maximum distance from the point in meters.

### Indexing in MongoDB

#### Creating Indexes

- Indexes support efficient query execution by limiting the number of documents that MongoDB needs to **examine**.
- The syntax for creating an index is `db.collection.createIndex(keys, options)`, where `keys` specifies the field or fields to index.

**Example: Create an index on the `age` field**

```javascript
db.users.createIndex({ age: 1 })
```

Use `1` for ascending order and `-1` for **descending** order.

**Compound Indexes:**

Indexes can be created on multiple fields, known as compound indexes.

 ```javascript
 db.users.createIndex({ age: 1, city: 1 })
 ```

### Types of Indexes

- **Single Field Indexes**: Indexes on a single field improve query performance on that field.
- **Compound Indexes**: Indexes on multiple fields support queries that sort or filter on multiple fields.
- **Multikey Indexes**: Indexes on array fields enable efficient querying of documents with array data.
- **Text Indexes**: Indexes that enable text search functionality over string content.
- **Geospatial Indexes**: Indexes that support geospatial queries for location data.

### Index Usage

Use the `explain()` method to understand how MongoDB executes a query and whether it utilizes an **index**.

```javascript
db.users.find({ age: 25 }).explain("executionStats")
```

- Analyze the output to check for `"stage": "IXSCAN"` to confirm index usage.
- Check `"nReturned"` and `"totalKeysExamined"` for insights into query **performance**.

**Monitoring Indexes:**

Use `db.collection.getIndexes()` to list all indexes on a collection.

```javascript
db.users.getIndexes()
```

**Dropping Indexes:**

Remove unnecessary indexes to optimize performance and reduce storage **overhead**.

```javascript
db.users.dropIndex("age_1")
```

