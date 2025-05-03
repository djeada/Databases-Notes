# Databases

Welcome to my database notes. I’ve put together insights on everything from database types and transactions to indexes, isolation levels, data warehousing, replication, and even the Halloween Problem. These notes are born from my own experiences and challenges, capturing both theory and practical tips in a concise, accessible way.

I update these files as I learn more and tackle new challenges in the world of databases. Your feedback or contributions are always welcome—if you see something that could be clearer or have additional ideas, please share. Let’s keep refining our understanding together.

![database_notes](https://github.com/user-attachments/assets/8a129873-7a0a-46d1-97cc-89608b83161b)

## Motivation

Throughout my career as an engineer, I have faced numerous challenges such as slow SQL queries, poorly optimized tables, and inefficient database architectures. Recognizing that a deep understanding of databases is essential for building reliable and high-performance data systems, I created this repository. It aims to serve as a comprehensive resource for myself and others to overcome database challenges and advance our skills in database engineering.

By compiling essential concepts, practical tools, and real-world case studies, this guide provides a well-rounded understanding of database systems. Whether you're looking to optimize queries, design robust schemas, or ensure data security, this repository offers valuable insights and actionable knowledge.

## Getting Started with Databases

Setting up a database can be challenging, especially if you're new to the field. To help you get started, here are some useful resources:

### Online SQL Interpreters

These platforms allow you to practice SQL queries directly in your browser without any local installation:

- **[SQLite Online](https://sqliteonline.com/):** Run SQLite queries online.
- **[SQL Practice](https://www.sql-practice.com/):** Practice SQL queries with instant feedback.
- **[SQL Forever](http://sqlforever.com/):** An online SQL interpreter.
- **[DB Fiddle](https://dbfiddle.uk/):** Test SQL queries across different database systems.

### Sample Databases

Working with sample databases is an excellent way to learn and experiment:

- **[PostgreSQL Sample Databases](https://wiki.postgresql.org/wiki/Sample_Databases):** A collection of sample databases for PostgreSQL.
- **[MySQL Sample Databases](https://dev.mysql.com/doc/index-other.html):** Sample databases provided by MySQL.
- **[Sakila Sample Database](https://dev.mysql.com/doc/sakila/en/):** A sample database for MySQL featuring a video rental store.

These resources provide a hands-on approach to learning, allowing you to experiment with SQL queries and explore different database systems.

## Notes

### Introduction to Databases

| Topic                              | Description                                                                                      | Notes                                                                                                     |
| ---------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Databases Introduction             | An overview of what databases are and their fundamental concepts.                                 | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/01_databases_intro.md) |
| Types of Databases                 | Exploring various kinds of databases, such as relational, NoSQL, and more.                        | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/02_types_of_databases.md) |
| Database Management Systems (DBMS) | Delves into systems that manage databases, their functions, and types.                            | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/03_database_management_systems_dbms_.md) |
| Data Models                        | Discusses different methods of structuring and representing data within a database.               | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/04_data_models.md) |
| Glossary                           | A compilation of key terms and definitions related to databases.                                  | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/05_glossary.md) |

### Database Design

| Topic                          | Description                                                                                                | Notes                                                                                                     |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Requirements Analysis          | Process of determining user needs and conditions for the development of a new database system.              | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/01_requirements_analysis.md) |
| Normalization                  | Techniques to minimize redundancy and dependency by organizing fields and tables of a database.             | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/02_normalization.md) |
| Denormalization                | Strategies to optimize database performance by selectively introducing redundancy and organizing tables.    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/03_denormalization.md) |
| Indexing Strategies            | Approaches to optimize the performance of database queries using indexes.                                  | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/04_indexing_strategies.md) |
| Data Integrity and Constraints | Ensuring the accuracy and consistency of data in a database and the rules governing permissible operations. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/05_data_integrity.md) |

### SQL

| Topic                             | Description                                                                                                              | Notes                                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Introduction to SQL               | An overview of SQL, its history, and its significance in database management.                                             | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/01_intro_to_sql.md) |
| Data Definition Language (DDL)    | Commands used to define and manage database structures, such as CREATE, ALTER, and DROP.                                  | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/02_data_definition_language_ddl.md) |
| Data Manipulation Language (DML)  | Commands for accessing and manipulating data, such as SELECT, INSERT, UPDATE, and DELETE.                                 | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/03_data_manipulation_language_dml.md) |
| Data Control Language (DCL)       | Commands related to data security, such as GRANT and REVOKE permissions.                                                  | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/04_data_control_language_dcl.md) |
| Transaction Control Language (TCL)| Commands that manage transactions in a database, such as COMMIT, ROLLBACK, and SAVEPOINT.                                 | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/05_transaction_control_language_tcl.md) |
| Joins, Subqueries, and Views      | Techniques to combine data from different tables and create virtual tables or complex queries in SQL.                     | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/06_joins_subqueries_and_views.md) |
| Stored Procedures and Functions   | Reusable SQL code saved in the database to perform specific tasks or calculations.                                        | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/07_stored_procedures_and_functions.md) |
| Triggers                          | Automated actions that are executed in response to specific changes in the database.                                      | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/08_triggers.md) |
| Hierarchical Data                 | Techniques and strategies to represent tree-like data structures in relational databases.                                 | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/09_hierarchical_data.md) |

### ACID Properties and Transactions

| Topic                             | Description                                                                                                           | Notes                                                                                                     |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| What is a Transaction             | An overview of what database transactions are and their significance in ensuring reliable data operations.            | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/01_transactions_intro.md) |
| Atomicity                         | Discusses the all-or-nothing nature of transactions, ensuring that operations are either fully completed or fully reverted. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/02_atomicity.md) |
| Consistency                       | Ensuring that transactions maintain database integrity and do not violate predefined rules or constraints.             | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/03_consistency.md) |
| Isolation                         | How transactions operate independently and how their effects can be isolated from other concurrent transactions.       | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/04_isolation.md) |
| Durability                        | How the results of a transaction are permanent and cannot be lost once committed.                                      | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/05_durability.md) |

### Database Storage and Indexing

| Topic                                             | Description                                                                                                      | Notes                                                                                                     |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| How Tables and Indexes are Stored on Disk         | Explores the underlying mechanisms databases use to store tables and indexes on disk, including physical layouts and data structures. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/01_how_tables_and_indexes_are_stored_on_disk.md) |
| Row-based vs. Column-based Databases              | Compares the two storage formats, discussing the advantages and drawbacks of each in terms of performance and use cases. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/02_row_based_vs_column_based_databases.md) |
| Primary Key vs. Secondary Key                     | Differentiates between primary and secondary keys, focusing on their roles, characteristics, and impact on performance. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/03_primary_key_vs_secondary_key.md) |
| Database Pages                                    | Explains how databases use pages to store data and facilitate efficient read/write operations.                    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/04_database_pages.md) |
| Indexing                                          | Provides an overview of indexing strategies, types of indexes, and how they enhance query performance.            | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/05_indexing.md) |

### Distributed Databases

| Topic                        | Description                                                                                                   | Notes                                                                                                     |
| -----------------------------| ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Partitioning Types           | Different methods of dividing a database into parts and distributing them across a system.                    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/01_types_of_partitioning.md) |
| Working with Billion-Row Tables | Techniques and best practices for efficiently handling and querying massive tables.                        | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/02_working_with_billion_row_table.md) |
| Consistent Hashing           | A technique used in distributing data across multiple servers, ensuring minimal rehashing when servers change.| [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/03_consistent_hashing.md) |
| Sharding                     | The process of breaking up large tables into smaller chunks and distributing them across multiple servers.    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/04_sharding.md) |
| Partitioning vs. Sharding    | Discussing the differences, similarities, and appropriate use-cases for partitioning and sharding.            | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/05_partitioning_vs_sharding.md) |
| CAP Theorem                  | A principle outlining the trade-offs between consistency, availability, and partition tolerance in distributed databases. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/06_cap_theorem.md) |
| Eventual Consistency         | A consistency model that ensures all replicas eventually converge to the same value.                          | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/07_eventual_consistency.md) |
| Distributed Database Systems | Overview of systems and architectures that support databases spread across multiple machines or locations.    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/08_distributed_database_systems.md) |

### Concurrency Control and Locking

| Topic                      | Description                                                                                 | Notes                                                                                                     |
| ---------------------------|---------------------------------------------------------------------------------------------| --------------------------------------------------------------------------------------------------------- |
| Shared vs. Exclusive Locks  | Differences between shared and exclusive locking mechanisms.                               | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/01_shared_vs_exclusive_locks.md) |
| Deadlocks                  | Understanding and resolving situations where locks block each other.                        | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/02_deadlocks.md) |
| Two-Phase Locking          | The protocol for acquiring and releasing locks to ensure consistency.                       | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/03_two_phase_locking.md) |
| Double Booking Problem     | Issues arising from concurrent transactions booking the same resource.                      | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/04_double_booking_problem.md) |
| Serializable vs. Repeatable Read  | Discusses the differences between isolation levels and their impact on concurrency and consistency. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/05_serializable_vs_repeatable_read.md) |

### Database Performance and Optimization

| Topic                          | Description                                                  | Notes                                                                                                     |
| -------------------------------|--------------------------------------------------------------| --------------------------------------------------------------------------------------------------------- |
| Query Optimization Techniques  | Methods to enhance the efficiency of database queries.       | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/01_query_optimization_techniques.md) |
| Indexing Strategies            | Techniques for using indexes to speed up query performance.  | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/02_indexing_strategies.md) |
| Database Caching               | Storing data in cache to improve retrieval times.            | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/03_database_caching.md) |
| Materialized Views             | Precomputed views for faster data access.                    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/04_materialized_views.md) |
| Accessing Databases in Code    | Best practices for database interactions within applications.| [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/05_accessing_database_in_code.md) |

### Database Replication

| Topic                                      | Description                                         | Notes                                                                                                     |
| -------------------------------------------|-----------------------------------------------------| --------------------------------------------------------------------------------------------------------- |
| Introduction to Replication                | Overview of database replication concepts.          | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/01_intro_to_replication.md) |
| Master-Standby Replication                 | Exploring the master-standby replication method.    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/02_master_standby_replication.md) |
| Multi-Master Replication                   | Delving into multi-master replication techniques.   | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/03_multi_master_replication.md) |
| Synchronous vs. Asynchronous Replication   | Comparing synchronous and asynchronous replication. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/04_synchronous_vs_asynchronous_replication.md) |

### NoSQL Databases

| Topic                       | Description                                           | Notes                                                                                                     |
| ----------------------------|-------------------------------------------------------| --------------------------------------------------------------------------------------------------------- |
| Introduction to NoSQL Databases | Introduction to non-relational database concepts.     | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/01_nosql_databases_intro.md) |
| Types of NoSQL Databases    | Overview of various NoSQL database types, such as key-value stores, document stores, column-family stores, and graph databases. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/02_types_of_nosql_databases.md) |
| Querying NoSQL Databases    | Techniques for querying non-relational databases.     | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/03_querying_nosql_databases.md) |
| CRUD Operations in SQL vs. NoSQL       | Differences in CRUD operations between SQL and NoSQL databases. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/04_crud_in_sql_vs_nosql.md) |

### Database Security and Best Practices

| Topic                              | Description                                        | Notes                                                                                                     |
| ---------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Backup and Recovery Strategies     | Strategies to backup and restore database data.    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/01_backup_and_recovery_strategies.md) |
| Database Security                  | Measures to protect data and maintain its integrity.| [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/02_database_security.md) |
| Capacity Planning                  | Predicting and addressing database growth needs.    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/03_capacity_planning.md) |
| Database Migration                 | Process of moving a database from one environment to another.| [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/04_database_migration.md) |
| Performance Monitoring and Tuning  | Observing and optimizing database performance.     | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/05_performance_monitoring_and_tuning.md) |
| Real-life Challenges               | Practical issues faced when managing databases.    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/06_real_life_challenges.md) |
| SQL Injection                      | A type of security vulnerability in database applications.| [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/07_sql_injection.md) |

### Database Engines

| Topic                     | Description                                                                                                      | Notes                                                                                                     |
| --------------------------| ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| SQLite                    | A lightweight, serverless SQL database engine commonly used in mobile apps and small-scale applications.         | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/01_sqlite.md) |
| MySQL                     | A widely-used, open-source relational database management system known for its performance and reliability.      | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/02_mysql.md) |
| PostgreSQL                | An advanced, open-source relational database system supporting complex queries and data types.                   | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/03_postgresql.md) |
| MongoDB                   | A popular NoSQL database designed for scalability and flexibility, using JSON-like documents.                    | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/04_mongodb.md) |
| Neo4j                     | A leading graph database that uses nodes and relationships to represent and store data for complex relationship querying. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/05_neo4j.md) |
| AWS Database Services     | Overview of Amazon Web Services' database offerings, covering both relational and non-relational services like Amazon RDS, DynamoDB, and Aurora. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/06_aws_services.md) |
| Choosing the Right Database | Guidelines and factors to consider when selecting a database engine for specific application needs and scenarios. | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/07_choosing_database.md) |

## Additional Topics

To further enhance your understanding of databases, consider exploring the following topics:

### Big Data and Data Warehousing

| Topic                    | Description                                                                                                      | Notes                                                                                                     |
| -------------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Data Warehousing         | Concepts and architectures for data warehouses used in large-scale data analytics.                               | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/13_big_data/01_data_warehousing.md) |
| Hadoop and HDFS          | An introduction to Hadoop and the Hadoop Distributed File System for big data storage and processing.             | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/13_big_data/02_hadoop_and_hdfs.md) |
| Spark SQL                | Using Apache Spark for large-scale data processing with SQL queries.                                              | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/13_big_data/03_spark_sql.md) |

### Object-Relational Mapping (ORM)

| Topic                 | Description                                                                                                | Notes                                                                                                     |
| ----------------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Introduction to ORM   | Understanding how ORMs bridge the gap between object-oriented programming and relational databases.        | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/14_orm/01_introduction_to_orm.md) |
| Popular ORM Tools     | Overview of popular ORM tools like Hibernate, Entity Framework, and SQLAlchemy.                             | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/14_orm/02_popular_orm_tools.md) |
| Advantages and Disadvantages of ORMs | Discussing when to use ORMs and potential performance considerations.                       | [Link](https://github.com/djeada/Databases-Notes/blob/main/notes/14_orm/03_advantages_and_disadvantages_of_orms.md) |

## References

### Books
- **Silberschatz, Abraham; Korth, Henry F.; Sudarshan, S.**  
  *Database System Concepts, 7th Edition*  
  [Amazon Link](https://amzn.to/4jrbQPX)

- **Date, C.J.**  
  *SQL and Relational Theory: How to Write Accurate SQL Code*  
  [Amazon Link](https://amzn.to/42myfag)

- **Redmond, Eric; Wilson, Jim R.**  
  *Seven Databases in Seven Weeks: A Guide to Modern Databases*  
  [Amazon Link](https://amzn.to/3R2vl5c)

- **Garcia-Molina, Hector; Ullman, Jeffrey D.; Widom, Jennifer.**  
  *Database Systems: The Complete Book*  
  [Amazon Link](https://amzn.to/4j3Qati)

- **Sadalage, Pramod J.; Fowler, Martin.**  
  *NoSQL Distilled: A Brief Guide to the Emerging World of Polyglot Persistence*  
  [Amazon Link](https://amzn.to/4i54Oiu)

### Online Courses and Resources
- [Cornell University CS4320](https://www.cs.cornell.edu/courses/cs4320/): Database Systems course materials.
- [Carnegie Mellon University 15-445/645 Database Systems](https://15445.courses.cs.cmu.edu/fall2023/): Comprehensive course on database systems.
- [SQL Exercises](https://pgexercises.com/): Practice SQL queries with practical exercises.
- [SQL Tutorial](http://www.sql-tutorial.ru/): In-depth SQL tutorials and examples.
- [Why are NoSQL Databases More Scalable than SQL?](https://softwareengineering.stackexchange.com/questions/194340/why-are-nosql-databases-more-scalable-than-sql/194408#194408): Discussion on scalability differences.
- [SQLZoo](https://sqlzoo.net/wiki/SQL_Tutorial): Interactive SQL tutorials.
- [How Databases Work](http://coding-geek.com/how-databases-work/): Explanation of database internals.
- [Database and SQL Cheat Sheet for Interviews](https://algodaily.com/lessons/databases-and-sql-cheat-sheet-for-interviews): Quick reference for interviews.
- [DataLemur SQL Interview Questions](https://datalemur.com/sql-interview-questions): Practice SQL questions for interviews.
- [Understanding Joins](https://joins.spathon.com/): Visual guide to SQL joins.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=djeada/Databases-Notes&type=Date)](https://star-history.com/#djeada/Databases-Notes&Date)

---

This repository is a living document and will be continually updated with new topics and resources. Contributions are welcome!
