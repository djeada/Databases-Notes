# Databases
This repository is a helpful guide for anyone working with data. It covers everything you need to know about databases, including SQL and NoSQL databases, making them faster, and keeping them secure. It also has real-world examples to help you understand how to use databases in practice.

## Motivation

I created this repository to help myself and others overcome database challenges and build reliable, high-performance data systems. Throughout my career, I've faced numerous database issues, including slow SQL queries and poorly optimized tables. I realized that having a deep understanding of databases is essential for creating effective data systems.

To improve my skills and tackle these challenges, I decided to create a comprehensive guide to databases. I've included essential concepts, tools, and real-world case studies to provide a well-rounded understanding of database engineering. 

## How to Setup a Database

Setting up a database can be a challenging task, especially if you're new to databases. However, to make it easier, here are a few helpful resources:

Sql interpreters online:

* https://sqliteonline.com/
* https://www.sql-practice.com/
* http://sqlforever.com/
* https://dbfiddle.uk/

Sample Databases:

* https://wiki.postgresql.org/wiki/Sample_Databases

These online SQL interpreters allow you to test SQL queries without the need for any local installation, making it easy to get started. The sample databases provide a useful starting point for testing and exploring different database systems.

## Notes

### Introduction to Databases

| Topic                                  | Description                                                                               | Notes                                                                                                     |
| -------------------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Databases Intro                        | An overview of what databases are and their fundamental concepts.                          | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/01_databases_intro.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /></a> |
| Types of Databases                     | Exploring various kinds of databases, such as relational, NoSQL, and more.                | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/02_types_of_databases.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /></a> |
| Database Management Systems (DBMS)     | Delves into systems that manage databases, their functions, and types.                     | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/03_database_management_systems_dbms_.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /></a> |
| Data Models                            | Discusses different methods of structuring and representing data within a database.       | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/04_data_models.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /></a> |
| Glossary                               | A compilation of key terms and definitions related to databases.                          | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/05_glossary.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /></a> |

### Database Design

| Topic                          | Description                                                                                               | Notes                                                                                                     |
| ------------------------------ | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Requirements Analysis          | Process of determining user needs and conditions for the development of a new database system.             | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/01_requirements_analysis.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Normalization         | A technique to minimize redundancy and dependency by organizing fields and table of a database.           | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/02_normalization.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Denormalization         | A technique to optimize database performance by selectively introducing redundancy and organizing tables.           | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/03_denormalization.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Indexing Strategies            | Approaches to optimize the performance of database queries using indexes.                                 | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/04_indexing_strategies.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Data Integrity and Constraints | Ensuring the accuracy and consistency of data in a database and the rules governing permissible database operations. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/05_data_integrity.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### SQL

| Topic                             | Description                                                                                                              | Notes                                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Intro to SQL                      | An overview of SQL, its history, and its significance in database management.                                             | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/01_intro_to_sql.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Data Definition Language (DDL)    | Commands used to define and manage database structures, such as CREATE, ALTER, and DROP.                                 | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/02_data_definition_language_ddl.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Data Manipulation Language (DML)  | Commands for accessing and manipulating data, such as SELECT, INSERT, UPDATE, and DELETE.                                 | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/03_data_manipulation_language_dml.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Data Control Language (DCL)       | Commands related to data security, such as GRANT and REVOKE permissions.                                                  | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/04_data_control_language_dcl.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Transaction Control Language (TCL)| Commands that manage transactions in a database, such as COMMIT, ROLLBACK, and SAVEPOINT.                                | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/05_transaction_control_language_tcl.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Joins, Subqueries, and Views      | Techniques to combine data from different tables and create virtual tables or complex queries in SQL.                      | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/06_joins_subqueries_and_views.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Stored Procedures and Functions   | Reusable SQL code saved in the database to perform specific tasks or calculations.                                        | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/07_stored_procedures_and_functions.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Triggers                          | Automated actions that are executed in response to specific changes in the database.                                      | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/08_triggers.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Hierarchical Data                 | Techniques and strategies to represent tree-like data structures in relational databases.                                  | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/09_hierarchical_data.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### ACID Properties and Transactions

| Topic                             | Description                                                                                                      | Notes                                                                                                     |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| What is a Transaction             | An overview of what database transactions are and their significance in ensuring reliable data operations.      | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/01_transactions_intro.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Atomicity                         | Discusses the all-or-nothing nature of transactions, ensuring that operations are either fully completed or fully reverted. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/02_atomicity.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Consistency                       | Delves into ensuring that transactions maintain database integrity and do not violate predefined rules or constraints. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/03_consistency.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Isolation                         | Discusses how transactions operate independently and how their effects can be isolated from other concurrent transactions. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/04_isolation.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Durability                        | Explores how the results of a transaction are permanent and cannot be lost once committed. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/05_durability.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### Database Storage and Indexing

| Topic                                             | Description                                                                                                      | Notes                                                                                                     |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| How Tables and Indexes are Stored on Disk         | Explores the underlying mechanisms databases use to store tables and indexes on disk, including physical layouts and data structures. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/01_how_tables_and_indexes_are_stored_on_disk.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Row-based vs. Column-based Databases              | Compares the two storage formats, discussing the advantages and drawbacks of each, especially in terms of performance and use cases. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/02_row_based_vs_column_based_databases.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Primary Key vs. Secondary Key                     | Differentiates between the primary and secondary keys, focusing on their roles, characteristics, and how they impact database performance and design. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/03_primary_key_vs_secondary_key.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Database Pages                                    | Delves into the concept of database pages, explaining how they are used to store data and facilitate efficient read/write operations. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/04_database_pages.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Indexing                                          | Provides an overview of indexing strategies, types of indexes, and how they enhance query performance by reducing data search times. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/05_indexing.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### Distributed Databases

| Topic                        | Description                                                                                                   | Notes                                                                                                     |
| -----------------------------| ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Partitioning Types           | Different methods of dividing a database or its elements into parts and distributing them across a system.    | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/01_types_of_partitioning.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Working with Billion-Row Table| Techniques and best practices for efficiently handling and querying massive tables.                           | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/02_working_with_billion_row_table.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Consistent Hashing           | A technique used in distributing data across multiple servers, ensuring minimal rehashing when servers are added or removed. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/03_consistent_hashing.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Sharding                     | The process of breaking up large tables into smaller chunks and distributing them across multiple servers.   | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/04_sharding.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Partitioning vs. Sharding    | Discussing the differences, similarities, and appropriate use-cases for partitioning and sharding.           | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/05_partitioning_vs_sharding.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| CAP Theorem                  | A principle outlining the trade-offs between consistency, availability, and partition tolerance in distributed databases. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/06_cap_theorem.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Eventual Consistency         | A consistency model which allows temporary inconsistencies but ensures that eventually all replicas converge to the same value. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/07_eventual_consistency.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Distributed Database Systems | Overview of the systems and architectures that support databases spread across multiple machines or locations.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/08_distributed_database_systems.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### Concurrency Control and Locking

| Topic                      | Description                                                | Notes                                                                                                                               |
| ---------------------------|------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------- |
| Shared vs. Exclusive Locks  | Differences between shared and exclusive locking mechanisms.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/01_shared_vs_exclusive_locks.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Deadlocks                  | Understanding and resolving situations where locks block each other.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/02_deadlocks.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Two-Phase Locking          | The protocol for acquiring and releasing locks to ensure consistency.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/03_two_phase_locking.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Double Booking Problem     | Issues arising from concurrent transactions booking the same resource.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/04_double_booking_problem.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Phantom Reads                     | An exploration of a specific concurrency issue where a transaction reads different rows after a subsequent read due to inserts or deletes by a concurrent transaction. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/05_phantom_reads.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Serializable vs. Repeatable Read  | Discusses the difference between two isolation levels in databases and their impact on concurrency and consistency. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/06_serializable_vs_repeatable_read.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### Database Performance and Optimization

| Topic                          | Description                                                  | Notes                                                                                                                                    |
| -------------------------------|--------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------ |
| Query Optimization Techniques  | Methods to enhance the efficiency of database queries.       | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/01_query_optimization_techniques.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Indexing Strategies            | Techniques for using indexes to speed up query performances. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/02_indexing_strategies.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Database Caching               | Storing data in cache to improve retrieval times.            | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/03_database_caching.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Materialized Views             | Precomputed views for faster data access.                    | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/04_materialized_views.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Accessing Database in Code     | Best practices for database interactions within applications.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/05_accesing_database_in_code.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### Database Replication

| Topic                                      | Description                                         | Notes                                                                                                                               |
| -------------------------------------------|----------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------- |
| Introduction to Replication                | Overview of database replication concepts.         | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/01_intro_to_replication.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Master-Standby Replication                 | Exploring the master-standby replication method.   | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/02_master_standby_replication.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Multi-Master Replication                   | Delving into multi-master replication techniques.  | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/03_multi_master_replication.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Synchronous vs. Asynchronous Replication   | Comparing synchronous and asynchronous replication. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/04_synchronous_vs_asynchronous_replication.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### NoSQL Databases

| Topic                       | Description                                           | Notes                                                                                                     |
| ----------------------------|-------------------------------------------------------| --------------------------------------------------------------------------------------------------------- |
| NoSQL Databases Intro       | Introduction to non-relational database concepts.     | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/01_nosql_databases_intro.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Types of NoSQL Databases    | Overview of various NoSQL database types.              | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/02_types_of_nosql_databases.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Querying NoSQL Databases    | Techniques for querying non-relational databases.     | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/03_querying_nosql_databases.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| CRUD in SQL vs. NoSQL       | Differences in CRUD operations between SQL and NoSQL. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/04_crud_in_sql_vs_nosql.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### Database Security and Best Practices

| Topic                              | Description                                        | Notes                                                                                                     |
| ---------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Backup and Recovery Strategies     | Strategies to backup and restore database data.    | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/01_backup_and_recovery_strategies.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Database Security                  | Measures to protect data and maintain its integrity.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/02_database_security.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Capacity Planning                  | Predicting and addressing database growth needs.    | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/03_capacity_planning.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Database Migration                 | Process of moving a database from one environment to another.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/04_database_migration.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Performance Monitoring and Tuning  | Observing and optimizing database performance.     | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/05_performance_monitoring_and_tuning.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Real-life Challenges               | Practical issues faced when managing databases.    | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/06_real_life_challanges.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| SQL Injection                      | A type of security vulnerability in database applications.| <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/07_sql_injection.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

### Database Engines

| Topic                     | Description                                                                                                      | Notes                                                                                                     |
| --------------------------| ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| SQLite                    | A lightweight, serverless, self-contained SQL database engine commonly used in mobile apps and small-scale applications. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/01_sqlite.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| MySQL                     | A widely-used, open-source relational database management system known for its fast performance and reliability. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/02_mysql.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| PostgreSQL                | An advanced, enterprise-class open-source relational database system supporting both SQL and procedural languages. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/03_postgresql.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| MongoDB                   | A popular NoSQL database, designed for scalability and flexibility, favoring JSON-like documents for data representation. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/04_mongodb.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Neo4j                     | A leading graph database that utilizes nodes and relationships to represent and store data for complex relationships. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/05_neo4j.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| AWS Services              | Overview of Amazon Web Services' database offerings, covering both relational and non-relational database services. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/06_aws_services.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |
| Choosing Database         | Guidelines and factors to consider when selecting a database engine for specific application needs and scenarios. | <a href="https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/07_choosing_database.md"><img src="https://img.icons8.com/color/344/markdown.png" height="50" /> </a> |

## References

* https://www.coursehero.com/sitemap/schools/11-Cornell-University/courses/44816-CS4320/
* https://15445.courses.cs.cmu.edu/fall2023/
* https://pgexercises.com/
* http://www.sql-tutorial.ru/
* https://softwareengineering.stackexchange.com/questions/194340/why-are-nosql-databases-more-scalable-than-sql/194408#194408
* https://sqlzoo.net/wiki/SQL_Tutorial
* http://coding-geek.com/how-databases-work/
* https://algodaily.com/lessons/databases-and-sql-cheat-sheet-for-interviews
* https://datalemur.com/sql-interview-questions
* Check this link out if you have a trouble understanding JOINS: https://joins.spathon.com/
  
