## SQLite

SQLite is a self-contained, serverless, and zero-configuration SQL database engine that's known for its simplicity and efficiency. Unlike traditional databases that require a separate server to operate, SQLite operates directly on ordinary disk files. This makes it an ideal choice for small to medium-sized applications, embedded systems, and situations where simplicity and ease of setup are paramount.

### Features

#### Serverless and Self-Contained

One of the key advantages of SQLite is that it doesn't require a separate server process. The entire database is stored in a single file on disk, which means you don't need to install or configure a database server to get started. This single-file database makes it incredibly portable and easy to share or move around.

#### Transactional

SQLite supports full ACID (Atomicity, Consistency, Isolation, Durability) transactions. This means you can trust that your data will remain consistent, even in the event of a system crash or power failure. Transactions in SQLite ensure that either all changes are committed, or none are, preserving the integrity of your data.

#### Cross-Platform Compatibility

Whether you're developing on Windows, macOS, Linux, or Android, SQLite works seamlessly across different operating systems. This cross-platform support makes it a versatile choice for developers who need their applications to run in diverse environments without worrying about database compatibility issues.

#### Small Footprint

With its minimal memory and storage requirements, SQLite is perfect for embedded systems and mobile applications where resources are limited. Its compact size doesn't compromise its capabilities, allowing you to perform complex queries and operations efficiently without burdening the system.

#### Extensive Language Support

SQLite provides APIs for a wide range of programming languages, including C, C++, Java, Python, and more. This extensive language support means you can integrate SQLite into your projects regardless of the programming language you're using, making it a flexible tool for developers.

#### Public Domain and Open Source

Released into the public domain, SQLite is free to use for any purpose, commercial or personal. There are no licensing fees or restrictions, which makes it an accessible option for organizations of all sizes. Being open source also means that the community can contribute to its development and improvement.

### Limitations

While SQLite is powerful and convenient, it's important to be aware of its limitations to ensure it's the right fit for your project.

#### Not Ideal for Large Applications

For applications that require handling large volumes of data (in 100s of TB) or need to scale extensively, SQLite might not be sufficient. Databases like MySQL or PostgreSQL are better suited for large-scale applications with high concurrency requirements.

#### Limited Concurrency

SQLite uses file-level locking during write operations, which means that while one process is writing to the database, other processes must wait. This can lead to contention in multi-user applications where simultaneous writes are common.

#### Lack of User Management and Access Control

Unlike larger database systems, SQLite doesn't have built-in support for user authentication or role-based access control. This means that security must be managed at the application level or through the operating system's file permissions.

#### Subset of SQL Features

SQLite supports most of the SQL standard but lacks some advanced features. For example, it doesn't support RIGHT OUTER JOIN or full ALTER TABLE capabilities, which might be necessary for certain complex database operations.

### Serverless Architecture

SQLite supports a serverless architecture by embedding the database engine directly within the application, eliminating the need for a separate server process. In this design, each client application accesses a shared, file-based database directly, relying on internal mechanisms such as file locking to handle concurrent access and maintain data integrity. This approach simplifies deployment and configuration because there is no centralized database server to install or manage, making SQLite an attractive solution for lightweight applications and environments where ease of use, portability, and minimal overhead are key considerations.

```
+-----------------------+        
|   Client 1            | -----------------------
| (App + SQLite)        |                       |
+-----------------------+                       |
         |                                      |
         V                                      V
+-----------------------+        +-------------------------------+
|   Client 2            | ---->  |    SQLite Database File       |
| (App + SQLite)        |        |  (Serverless, File-Based DB)  |
+-----------------------+        +-------------------------------+
         |                                      Ʌ
         V                                      |
+-----------------------+                       |
|   Client 3            | -----------------------
| (App + SQLite)        |
+-----------------------+
```

The SQLite database file is organized into several key sections that together ensure efficient data storage and retrieval. At the beginning of the file, the **File Header** stores essential metadata such as page size and version information. Following this, the **Page Directory** maps out the locations of various pages within the file. The **Data Pages** contain the actual records for database tables, while the **Index Pages** hold index entries that accelerate query processing. Lastly, the **Free Pages** represent unallocated space available for future data storage.

```
+-----------------------------------+
|           SQLite File             |
+-----------------------------------+
|           File Header             |
+-----------------------------------+
|          Page Directory           |
+-----------------------------------+
|          Data Pages               |
+-----------------------------------+
|         Index Pages               |
+-----------------------------------+
|            Free Pages             |
+-----------------------------------+
```

### Use Cases

SQLite is well-suited for a variety of applications where simplicity and efficiency are key.

- In **Embedded Systems**, devices with limited computing resources such as IoT sensors and microcontrollers benefit from SQLite's lightweight, serverless design, which efficiently handles local data storage and retrieval.
- Due to its compact size and seamless integration capabilities, **Mobile Applications** frequently utilize SQLite on both Android and iOS platforms to manage offline data and improve user responsiveness.
- Developers working on **Desktop Applications** often prefer SQLite for its self-contained architecture, which simplifies the storage of user preferences and application settings without requiring the setup of a full-scale server.
- During the early phases of development, **Prototyping and Testing** are accelerated by SQLite’s ease of deployment and minimal configuration demands, enabling rapid iteration and validation of application concepts.

### SQLite Commands

Interacting with SQLite involves using SQL commands to manage and manipulate data. Below are some fundamental commands along with examples, outputs, and interpretations.

#### Creating a Database

Creating a SQLite database is as simple as opening a connection to a new file.

```bash
$ sqlite3 mydatabase.db
```

*Example Output:*

```
SQLite version 3.34.0 2020-12-01 16:14:00
Enter ".help" for usage hints.
sqlite>
```

- The SQLite version information confirms that SQLite has started.
- The `sqlite>` prompt indicates that the database is ready to accept SQL commands.

#### Creating Tables

Before storing data, you need to create a table to hold it.

```sql
sqlite> CREATE TABLE users (
   ...> id INTEGER PRIMARY KEY,
   ...> name TEXT NOT NULL,
   ...> email TEXT UNIQUE NOT NULL
   ...> );
```

*Example Output:*

```
sqlite>
```

o output means the table was created successfully without errors.

#### Inserting Data

Add data to your table using the `INSERT INTO` command.

```sql
sqlite> INSERT INTO users (name, email) VALUES ('Alice Smith', 'alice@example.com');
```

*Example Output:*

```
sqlite>
```

Successful insertion returns to the prompt without errors, indicating the data was added.

#### Querying Data

Retrieve data using the `SELECT` command.

```sql
sqlite> SELECT * FROM users;
```

*Example Output:*

```
1|Alice Smith|alice@example.com
```

*Interpretation of the Output:*

- **1**: The user's unique `id`.
- **Alice Smith**: The `name` of the user.
- **alice@example.com**: The user's `email` address.

#### Updating Data

Modify existing data with the `UPDATE` command.

```sql
sqlite> UPDATE users SET email = 'alice.smith@example.com' WHERE id = 1;
```

*Example Output:*

```
sqlite>
```

The absence of an error message indicates the email was updated successfully.

#### Deleting Data

Remove data using the `DELETE` command.

```sql
sqlite> DELETE FROM users WHERE id = 1;
```

*Example Output:*

```
sqlite>
```

*Interpretation of the Output:*

- Returning to the prompt without errors means the user was deleted successfully.

#### Dropping Tables

Delete an entire table with the `DROP TABLE` command.

```sql
sqlite> DROP TABLE users;
```

*Example Output:*

```
sqlite>
```

The table was dropped successfully since no error messages were displayed.

### SQLite Engine

SQLite's engine is designed to be simple yet effective, handling most common use cases efficiently without the complexity of managing different storage engines.

#### Single Storage Engine

SQLite uses a B-tree-based storage engine for both tables and indexes. This means that data is stored in a balanced tree structure, which allows for efficient data retrieval and storage. The entire database, including all tables and indexes, is contained within a single file, simplifying data management.

#### Journaling Modes

To ensure data integrity and support transactions, SQLite uses journaling. Journaling records changes before they're committed to the database, which helps prevent corruption in the event of a crash.

##### Types of Journaling Modes

| Mode                      | Description                                                                                                                                                                         |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DELETE**                | The default mode where the journal file is deleted after each transaction. It ensures data integrity but can be slower due to the overhead of file deletion.                      |
| **WAL (Write-Ahead Logging)** | Improves performance and allows for higher concurrency by writing changes to a separate log file. This is especially useful for applications with many read operations.       |
| **TRUNCATE**              | Similar to DELETE mode but truncates the journal file to zero length instead of deleting it, which can be faster on some filesystems.                                               |
| **PERSIST**               | Keeps the journal file but overwrites its header to indicate it's empty, reducing file system overhead.                                                                              |
| **MEMORY**                | Stores the journal in RAM, offering the best performance but at the risk of data loss if the application crashes.                                                                    |

#### In-Memory Databases

You can create a database entirely in memory, which is extremely fast but non-persistent.

```bash
$ sqlite3 :memory:
```

This command opens a temporary database that resides in RAM.

*Example Output:*

```
SQLite version 3.34.0 2020-12-01 16:14:00
Enter ".help" for usage hints.
sqlite>
```

An in-memory database is ready to use, but all data will be lost when the session ends.

#### File Storage Options

SQLite provides options to control how data is written to disk, affecting performance and durability.

##### Synchronization Modes

| Mode       | Description                                                                                                       |
|------------|-------------------------------------------------------------------------------------------------------------------|
| **FULL**   | Ensures all data is fully written to disk, providing maximum durability at the cost of speed.                     |
| **NORMAL** | Offers a balance between performance and durability by syncing less frequently than FULL.                         |
| **OFF**    | Maximizes performance by not syncing data to disk, which risks data loss if the system crashes.                    |

#### Temporary Databases

Create temporary databases that exist only for the duration of the session.

```bash
$ sqlite3 ""
```

*Example Output:*

```
SQLite version 3.34.0 2020-12-01 16:14:00
Enter ".help" for usage hints.
sqlite>
```

A temporary database is created, which is useful for testing or temporary data storage.

#### Virtual Tables

SQLite supports virtual tables, allowing you to create tables whose data isn't stored in the database file but is computed or retrieved from other sources.

##### Examples of Virtual Tables

- **FTS (Full-Text Search)**: Enables advanced text search capabilities within SQLite.
- **R-Tree**: Optimized for spatial data, allowing efficient querying of multi-dimensional data.
- **JSON1**: Allows storage and querying of JSON data within SQLite tables.
