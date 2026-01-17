<div align="center">

# 🗄️ Database Systems - Comprehensive Notes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/djeada/Databases-Notes?style=social)](https://github.com/djeada/Databases-Notes/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/djeada/Databases-Notes?style=social)](https://github.com/djeada/Databases-Notes/network/members)

**A comprehensive, practical guide to database systems—from fundamentals to advanced topics**

[📚 Browse Notes](#-notes) • [🚀 Quick Start](#-quick-start) • [💡 Features](#-features) • [📖 References](#-references) • [⭐ Star History](#-star-history)

![database_notes](https://github.com/user-attachments/assets/8a129873-7a0a-46d1-97cc-89608b83161b)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Motivation](#-motivation)
- [Quick Start](#-quick-start)
- [Features](#-features)
- [Notes](#-notes)
  - [Introduction to Databases](#1-introduction-to-databases)
  - [Database Design](#2-database-design)
  - [SQL](#3-sql)
  - [ACID Properties and Transactions](#4-acid-properties-and-transactions)
  - [Database Storage and Indexing](#5-database-storage-and-indexing)
  - [Distributed Databases](#6-distributed-databases)
  - [Concurrency Control and Locking](#7-concurrency-control-and-locking)
  - [Database Performance and Optimization](#8-database-performance-and-optimization)
  - [Database Replication](#9-database-replication)
  - [NoSQL Databases](#10-nosql-databases)
  - [Database Security and Best Practices](#11-database-security-and-best-practices)
  - [Database Engines](#12-database-engines)
  - [Big Data and Data Warehousing](#13-big-data-and-data-warehousing)
  - [Object-Relational Mapping (ORM)](#14-object-relational-mapping-orm)
- [References](#-references)
- [Contributing](#-contributing)
- [License](#-license)
- [Star History](#-star-history)

---

## 🎯 About

Welcome to this comprehensive collection of database notes! This repository contains insights on everything from database types and transactions to indexes, isolation levels, data warehousing, replication, and advanced topics like the CAP theorem and the Halloween Problem.

These notes are born from real-world experiences and challenges, capturing both theoretical foundations and practical tips in a concise, accessible format. The content is continuously updated as new challenges are tackled and knowledge is gained in the ever-evolving world of databases.

**Your feedback and contributions are always welcome!** If you see something that could be clearer or have additional ideas, please share. Let's keep refining our understanding together.

---

## 💡 Motivation

Throughout my career as an engineer, I have faced numerous challenges such as:
- 🐌 Slow SQL queries and inefficient indexes
- 🏗️ Poorly optimized table structures
- ⚙️ Inefficient database architectures
- 🔒 Complex transaction management and isolation issues

Recognizing that a deep understanding of databases is essential for building **reliable** and **high-performance** data systems, I created this repository. It aims to serve as a comprehensive resource for myself and others to overcome database challenges and advance our skills in database engineering.

By compiling essential concepts, practical tools, and real-world case studies, this guide provides a well-rounded understanding of database systems. Whether you're looking to optimize queries, design robust schemas, or ensure data security, this repository offers valuable insights and actionable knowledge.

---

## 🚀 Quick Start

Setting up a database can be challenging, especially if you're new to the field. Here are some resources to help you get started quickly:

### 🌐 Online SQL Interpreters

Practice SQL queries directly in your browser without any local installation:

| Platform | Description | Link |
|----------|-------------|------|
| **SQLite Online** | Run SQLite queries online | [sqliteonline.com](https://sqliteonline.com/) |
| **SQL Practice** | Practice SQL with instant feedback | [sql-practice.com](https://www.sql-practice.com/) |
| **SQL Forever** | Online SQL interpreter | [sqlforever.com](http://sqlforever.com/) |
| **DB Fiddle** | Test queries across different DBs | [dbfiddle.uk](https://dbfiddle.uk/) |

### 📊 Sample Databases

Working with sample databases is an excellent way to learn and experiment:

| Database | Description | Link |
|----------|-------------|------|
| **PostgreSQL Samples** | Collection of PostgreSQL sample DBs | [PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Sample_Databases) |
| **MySQL Samples** | Sample databases from MySQL | [MySQL Docs](https://dev.mysql.com/doc/index-other.html) |
| **Sakila Database** | Video rental store sample DB | [Sakila Docs](https://dev.mysql.com/doc/sakila/en/) |

---

## 💡 Features

✨ **Comprehensive Coverage**: From basic concepts to advanced distributed systems  
📝 **Practical Examples**: Real-world use cases and code samples  
🎓 **Learning Path**: Structured progression from beginner to advanced  
🔄 **Continuously Updated**: Regular updates with new topics and improvements  
🌟 **Community-Driven**: Open to contributions and feedback  
📖 **Well-Organized**: Easy-to-navigate structure with detailed table of contents  

---

## 📚 Notes

### 1. Introduction to Databases

| Topic | Description | Link |
|-------|-------------|------|
| �� **Databases Introduction** | Overview of database fundamentals and core concepts | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/01_databases_intro.md) |
| 🗂️ **Types of Databases** | Exploring relational, NoSQL, and other database types | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/02_types_of_databases.md) |
| 🖥️ **Database Management Systems** | Understanding DBMS functions and types | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/03_database_management_systems_dbms_.md) |
| 🏗️ **Data Models** | Methods of structuring and representing data | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/04_data_models.md) |
| 📚 **Glossary** | Key terms and definitions | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/05_glossary.md) |

### 2. Database Design

| Topic | Description | Link |
|-------|-------------|------|
| 📋 **Requirements Analysis** | Determining user needs for database development | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/01_requirements_analysis.md) |
| 🔄 **Normalization** | Minimizing redundancy through proper organization | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/02_normalization.md) |
| ⚡ **Denormalization** | Optimizing performance through strategic redundancy | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/03_denormalization.md) |
| 🔍 **Indexing Strategies** | Optimizing query performance with indexes | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/04_indexing_strategies.md) |
| ✅ **Data Integrity** | Ensuring accuracy and consistency of data | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/05_data_integrity.md) |

### 3. SQL

| Topic | Description | Link |
|-------|-------------|------|
| 🚀 **Introduction to SQL** | SQL history and significance | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/01_intro_to_sql.md) |
| 🏗️ **DDL - Data Definition** | CREATE, ALTER, DROP commands | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/02_data_definition_language_ddl.md) |
| ✏️ **DML - Data Manipulation** | SELECT, INSERT, UPDATE, DELETE | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/03_data_manipulation_language_dml.md) |
| 🔒 **DCL - Data Control** | GRANT and REVOKE permissions | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/04_data_control_language_dcl.md) |
| 🔄 **TCL - Transaction Control** | COMMIT, ROLLBACK, SAVEPOINT | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/05_transaction_control_language_tcl.md) |
| 🔗 **Joins, Subqueries & Views** | Combining data from multiple tables | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/06_joins_subqueries_and_views.md) |
| ⚙️ **Stored Procedures** | Reusable SQL code blocks | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/07_stored_procedures_and_functions.md) |
| 🎯 **Triggers** | Automated database actions | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/08_triggers.md) |
| 🌳 **Hierarchical Data** | Managing tree-like structures | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/03_sql/09_hierarchical_data.md) |

### 4. ACID Properties and Transactions

| Topic | Description | Link |
|-------|-------------|------|
| 💼 **What is a Transaction** | Overview of database transactions | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/01_transactions_intro.md) |
| ⚛️ **Atomicity** | All-or-nothing transaction property | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/02_atomicity.md) |
| 🎯 **Consistency** | Maintaining database integrity | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/03_consistency.md) |
| 🔐 **Isolation** | Independent transaction execution | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/04_isolation.md) |
| 💾 **Durability** | Permanent transaction results | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/04_acid_properties_and_transactions/05_durability.md) |

### 5. Database Storage and Indexing

| Topic | Description | Link |
|-------|-------------|------|
| 💿 **Storage on Disk** | How tables and indexes are physically stored | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/01_how_tables_and_indexes_are_stored_on_disk.md) |
| 📊 **Row vs Column Storage** | Comparing storage formats and performance | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/02_row_based_vs_column_based_databases.md) |
| 🔑 **Primary vs Secondary Keys** | Key types and their performance impact | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/03_primary_key_vs_secondary_key.md) |
| 📄 **Database Pages** | How databases use pages for I/O operations | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/04_database_pages.md) |
| 🔍 **Indexing** | Index types and optimization strategies | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/05_storage_and_indexing/05_indexing.md) |

### 6. Distributed Databases

| Topic | Description | Link |
|-------|-------------|------|
| 🏢 **Distributed Database Systems** | Overview of systems and architectures | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/01_distributed_database_systems.md) |
| 📂 **Partitioning** | Methods of dividing and distributing data | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/02_partitioning.md) |
| 🔀 **Sharding** | Breaking tables into distributed chunks | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/03_sharding.md) |
| ⚔️ **Partitioning vs Sharding** | Understanding the differences | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/04_partitioning_vs_sharding.md) |
| ⚖️ **Consistent Hashing** | Distributing data with minimal rehashing | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/05_consistent_hashing.md) |
| 🎭 **CAP Theorem** | Consistency, availability, partition tolerance | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/06_cap_theorem.md) |
| 🔄 **Eventual Consistency** | Convergence model for distributed systems | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/07_eventual_consistency.md) |
| 🌐 **Distributed Systems (Advanced)** | Advanced distributed database architectures | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/06_distributed_databases/08_distributed_database_systems.md) |

### 7. Concurrency Control and Locking

| Topic | Description | Link |
|-------|-------------|------|
| 🔓 **Shared vs Exclusive Locks** | Different locking mechanisms | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/01_shared_vs_exclusive_locks.md) |
| 🔒 **Deadlocks** | Understanding and resolving deadlock situations | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/02_deadlocks.md) |
| 🔐 **Two-Phase Locking** | Lock acquisition and release protocol | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/03_two_phase_locking.md) |
| 📅 **Double Booking Problem** | Concurrent resource booking challenges | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/04_double_booking_problem.md) |
| 🎚️ **Isolation Levels** | Serializable vs Repeatable Read | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/07_concurrency_control/05_serializable_vs_repeatable_read.md) |

### 8. Database Performance and Optimization

| Topic | Description | Link |
|-------|-------------|------|
| ⚡ **Query Optimization** | Enhancing query efficiency | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/01_query_optimization_techniques.md) |
| 🔍 **Indexing Strategies** | Using indexes for better performance | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/02_indexing_strategies.md) |
| 💾 **Database Caching** | Improving retrieval times with cache | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/03_database_caching.md) |
| 📊 **Materialized Views** | Precomputed views for faster access | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/04_materialized_views.md) |
| 💻 **Database Access in Code** | Best practices for application integration | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/08_database_performance/05_accessing_database_in_code.md) |

### 9. Database Replication

| Topic | Description | Link |
|-------|-------------|------|
| 📖 **Replication Introduction** | Overview of database replication concepts | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/01_intro_to_replication.md) |
| 🏢 **Master-Standby** | Primary-replica replication model | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/02_master_standby_replication.md) |
| 🔀 **Multi-Master** | Multiple active nodes replication | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/03_multi_master_replication.md) |
| ⚖️ **Sync vs Async** | Replication timing strategies | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/09_database_replication/04_synchronous_vs_asynchronous_replication.md) |

### 10. NoSQL Databases

| Topic | Description | Link |
|-------|-------------|------|
| 🌟 **NoSQL Introduction** | Non-relational database concepts | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/01_nosql_databases_intro.md) |
| 📋 **NoSQL Types** | Key-value, document, column, graph stores | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/02_types_of_nosql_databases.md) |
| 🔍 **Querying NoSQL** | Query techniques for non-relational DBs | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/03_querying_nosql_databases.md) |
| ⚖️ **CRUD: SQL vs NoSQL** | Comparing operations across paradigms | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/10_nosql_databases/04_crud_in_sql_vs_nosql.md) |

### 11. Database Security and Best Practices

| Topic | Description | Link |
|-------|-------------|------|
| 💾 **Backup & Recovery** | Strategies for data protection | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/01_backup_and_recovery_strategies.md) |
| 🔒 **Database Security** | Protecting data integrity and access | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/02_database_security.md) |
| 📈 **Capacity Planning** | Predicting and managing growth | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/03_capacity_planning.md) |
| 🚚 **Database Migration** | Moving databases between environments | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/04_database_migration.md) |
| 📊 **Performance Monitoring** | Observing and optimizing performance | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/05_performance_monitoring_and_tuning.md) |
| ⚠️ **SQL Injection** | Understanding and preventing SQL injection | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/06_sql_injection.md) |
| 🔧 **Crash Recovery** | Database crash recovery mechanisms | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/11_security_best_practices/07_crash_recovery_in_databases.md) |

### 12. Database Engines

| Topic | Description | Link |
|-------|-------------|------|
| 🪶 **SQLite** | Lightweight, serverless SQL database | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/01_sqlite.md) |
| 🐬 **MySQL** | Popular open-source RDBMS | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/02_mysql.md) |
| 🐘 **PostgreSQL** | Advanced open-source database system | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/03_postgresql.md) |
| 🍃 **MongoDB** | Document-oriented NoSQL database | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/04_mongodb.md) |
| 🔗 **Neo4j** | Leading graph database platform | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/05_neo4j.md) |
| ☁️ **AWS Database Services** | Cloud database offerings from AWS | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/06_aws_services.md) |
| 🎯 **Choosing a Database** | Selection criteria and decision factors | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/12_database_engines/07_choosing_database.md) |

### 13. Big Data and Data Warehousing

| Topic | Description | Link |
|-------|-------------|------|
| 🏭 **Data Warehousing** | Architectures for large-scale analytics | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/13_big_data/01_data_warehousing.md) |
| 🐘 **Hadoop & HDFS** | Distributed file system for big data | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/13_big_data/02_hadoop_and_hdfs.md) |
| ⚡ **Spark SQL** | Large-scale data processing with SQL | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/13_big_data/03_spark_sql.md) |

### 14. Object-Relational Mapping (ORM)

| Topic | Description | Link |
|-------|-------------|------|
| 🔗 **ORM Introduction** | Bridging OOP and relational databases | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/14_orm/01_introduction_to_orm.md) |
| 🛠️ **Popular ORM Tools** | Hibernate, Entity Framework, SQLAlchemy | [View](https://github.com/djeada/Databases-Notes/blob/main/notes/14_orm/02_popular_orm_tools.md) |

---

## 📖 References

### 📚 Books

<table>
<tr>
<td width="50%">

#### Database Fundamentals

- **[Database System Concepts (7th Edition)](https://amzn.to/4jrbQPX)**  
  *Silberschatz, Korth, Sudarshan*  
  Comprehensive coverage of database theory and practice

- **[Database Systems: The Complete Book](https://amzn.to/4j3Qati)**  
  *Garcia-Molina, Ullman, Widom*  
  In-depth exploration of database internals

</td>
<td width="50%">

#### Specialized Topics

- **[SQL and Relational Theory](https://amzn.to/42myfag)**  
  *C.J. Date*  
  Deep dive into SQL accuracy and theory

- **[Seven Databases in Seven Weeks](https://amzn.to/3R2vl5c)**  
  *Redmond, Wilson*  
  Guide to modern database paradigms

- **[NoSQL Distilled](https://amzn.to/4i54Oiu)**  
  *Sadalage, Fowler*  
  Brief guide to polyglot persistence

</td>
</tr>
</table>

### 🎓 Online Courses & Resources

#### University Courses
- 🎓 [Cornell CS4320](https://www.cs.cornell.edu/courses/cs4320/) - Database Systems
- 🎓 [CMU 15-445/645](https://15445.courses.cs.cmu.edu/fall2023/) - Comprehensive Database Systems Course

#### Interactive Learning
- 💻 [SQL Exercises](https://pgexercises.com/) - Practical SQL practice
- 💻 [SQLZoo](https://sqlzoo.net/wiki/SQL_Tutorial) - Interactive SQL tutorials
- 💻 [Understanding Joins](https://joins.spathon.com/) - Visual SQL join guide

#### Articles & Tutorials
- 📝 [How Databases Work](http://coding-geek.com/how-databases-work/) - Database internals explained
- 📝 [SQL Tutorial (Russian)](http://www.sql-tutorial.ru/) - Comprehensive SQL guide
- 📝 [NoSQL Scalability Discussion](https://softwareengineering.stackexchange.com/questions/194340/why-are-nosql-databases-more-scalable-than-sql/194408#194408)

#### Interview Preparation
- 📋 [Database & SQL Cheat Sheet](https://algodaily.com/lessons/databases-and-sql-cheat-sheet-for-interviews)
- 📋 [DataLemur SQL Questions](https://datalemur.com/sql-interview-questions)

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**!

### How to Contribute

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. ✍️ Make your changes and commit (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🎯 Open a Pull Request

### Contribution Guidelines

- ✅ Ensure content is accurate and well-researched
- ✅ Follow the existing document structure and formatting
- ✅ Include practical examples where applicable
- ✅ Add references for complex topics
- ✅ Check for spelling and grammar

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](license) file for details.

```
MIT License - Copyright (c) 2023 Adam Djellouli
```

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=djeada/Databases-Notes&type=Date)](https://star-history.com/#djeada/Databases-Notes&Date)

---

<div align="center">

**[⬆ Back to Top](#-database-systems---comprehensive-notes)**

Made with ❤️ by [Adam Djellouli](https://github.com/djeada)

*This repository is a living document and will be continually updated with new topics and resources.*

</div>
