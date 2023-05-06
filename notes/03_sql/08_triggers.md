
## Triggers

Triggers are stored procedures that automatically execute in response to specific events on certain tables or views. They can help maintain data integrity, enforce business rules, and audit data changes.

### Types of Triggers

Triggers can be classified by their execution timing and the event that initiates them:

1. **BEFORE**: Executes before the triggering event
2. **AFTER**: Executes after the triggering event
3. **INSTEAD OF**: Executes in place of the triggering event

Triggers can be associated with the following events:

1. **INSERT**: Activates when a new row is inserted into the table
2. **UPDATE**: Activates when a row in the table is updated
3. **DELETE**: Activates when a row is deleted from the table

### Creating a Trigger

To create a trigger, use the `CREATE TRIGGER` statement:

```sql
CREATE TRIGGER trigger_name
{BEFORE | AFTER | INSTEAD OF} {INSERT | UPDATE | DELETE}
ON table_name
[FOR EACH ROW]
[WHEN (condition)]
BEGIN
  -- SQL code
END;
```

- `BEFORE, AFTER, or INSTEAD OF`: Specifies when the trigger should be executed
- `INSERT, UPDATE, or DELETE`: Specifies the event that causes the trigger to fire
- `ON table_name`: Specifies the table or view associated with the trigger
- `FOR EACH ROW`: Optional, if specified, the trigger is row-level, otherwise it's statement-level
- `WHEN (condition)`: Optional, specifies a condition for the trigger to fire

### Modifying a Trigger

To modify a trigger, use the `ALTER TRIGGER` statement:

```sql
ALTER TRIGGER trigger_name
{BEFORE | AFTER | INSTEAD OF} {INSERT | UPDATE | DELETE}
ON table_name
[FOR EACH ROW]
[WHEN (condition)]
BEGIN
  -- SQL code
END;
```

### Deleting a Trigger

To delete a trigger, use the `DROP TRIGGER` statement:

```sql
DROP TRIGGER trigger_name;
```

### Triggers and Performance

Triggers can significantly impact performance, especially if they are poorly designed or multiple triggers activate on the same table. Exercise caution when using triggers and consider alternative options, such as stored procedures or application-level logic, before implementing them.
