## Querying NoSQL databases
Querying NoSQL databases requires a different approach compared to relational databases

## MongoDB Overview

### Data Model
- Stores data as BSON documents in collections
- Supports nested documents and arrays

### Query Language
- Uses JSON-like query syntax
- Supports various query operators and functions

## Basic Queries

### Find
- Retrieve documents from a collection based on filter criteria
- Syntax: `db.collection.find(query, projection)`
- Example: `db.users.find({age: 25})`

### Count
- Count the number of documents matching a query
- Syntax: `db.collection.count(query)`
- Example: `db.users.count({age: 25})`

### Distinct
- Retrieve distinct values for a specified field
- Syntax: `db.collection.distinct(field, query)`
- Example: `db.users.distinct("city", {age: 25})`

## Advanced Queries

### Aggregation
- Process documents and return computed results
- Syntax: `db.collection.aggregate(pipeline)`
- Example: `db.users.aggregate([{$group: {_id: "$city", count: {$sum: 1}}}])`

### Text Search
- Search for text within documents using a text index
- Syntax: `db.collection.find({$text: {$search: searchString}})`
- Example: `db.articles.find({$text: {$search: "NoSQL"}})`

### Geospatial Queries
- Query documents based on location data
- Syntax: `db.collection.find({location: {$near: {$geometry: point, $maxDistance: distance}}})`
- Example: `db.restaurants.find({location: {$near: {$geometry: {type: "Point", coordinates: [-73.9667, 40.78]}, $maxDistance: 1000}}})`

## Indexing
- Create indexes to improve query performance
- Syntax: `db.collection.createIndex(keys, options)`
- Example: `db.users.createIndex({age: 1})`

## Best Practices
- Understand the MongoDB data model and query language
- Use appropriate query operators and functions for the task at hand
- Create indexes to optimize query performance
- Continuously monitor and analyze MongoDB query performance to identify areas for improvement
