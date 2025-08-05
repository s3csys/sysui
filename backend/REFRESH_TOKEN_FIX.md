# Refresh Token Length Fix

## Issue

The application was encountering a database error when trying to store refresh tokens:

```
sqlalchemy.exc.DataError: (mysql.connector.errors.DataError) 1406 (22001): Data too long for column 'refresh_token' at row 1
```

This error occurs because the JWT refresh tokens being generated are longer than the 255 character limit defined in the database schema for the `refresh_token` column in the `session` table.

## Root Cause

The `refresh_token` column in the `session` table was defined as `String(255)` in the original database schema, but the JWT tokens being generated can exceed this length, especially when they include additional claims like fingerprint and IP address.

## Solution

The solution is to increase the length of the `refresh_token` column from `String(255)` to `String(512)` to accommodate larger JWT tokens.

### Implementation Details

1. The `Session` model in `app/models/user.py` has been updated to define the `refresh_token` column as `String(512)` instead of `String(255)`.

2. When the application is set up using the `setup.py` script or the `init_db.py` script, the database tables will be created with the updated column definition.

## How to Apply the Fix

For new installations, no additional steps are needed as the database will be created with the correct column size.

For existing installations, you have two options:

### Option 1: Direct SQL Modification

Execute the following SQL command on your database:

```sql
ALTER TABLE session MODIFY COLUMN refresh_token VARCHAR(512) NOT NULL;
```

### Option 2: Recreate the Database

If you can afford to lose existing data or have a backup:

1. Drop the existing database tables
2. Run the initialization script again:
   ```
   python -m scripts.init_db
   ```

## Verification

To verify that the fix has been applied, you can check the column definition in your database:

```sql
DESCRIBE session;
```

The `refresh_token` column should now show a length of 512.

## Future Recommendations

1. Consider using the `Text` type for tokens and other potentially long string values to avoid similar issues in the future.
2. Implement validation to ensure that tokens don't exceed the maximum allowed length before attempting to store them.
3. Add better error handling to provide more informative error messages when data length issues occur.