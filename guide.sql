-- This is a guide with examples for the accounts database
-- Each line starting with -- is a comment explaining what the code does

-- 1. How to insert a new account
-- Note: In real applications, you should NEVER store plain passwords
-- Always use proper password hashing (like bcrypt) before storing
INSERT INTO accounts (email, password_hash, status)
VALUES ('user@example.com', 'hashed_password_here', 'active');

-- 2. How to find an account by email
SELECT * FROM accounts WHERE email = 'user@example.com';

-- 3. How to update an account's status
UPDATE accounts 
SET status = 'suspended' 
WHERE email = 'user@example.com';

-- 4. How to list all active accounts
SELECT email, created_at 
FROM accounts 
WHERE status = 'active';

-- 5. How to delete an account
DELETE FROM accounts WHERE email = 'user@example.com';

-- Simple explanation of the database structure:
-- 1. The accounts table has these main columns:
--    - id: A unique number for each account (automatically assigned)
--    - email: The user's email address (must be unique)
--    - password_hash: The hashed password (for security)
--    - status: Can be 'active', 'inactive', or 'suspended'
--    - created_at: When the account was created
--    - updated_at: When the account was last updated

-- Common beginner tips:
-- 1. Always use single quotes (') for text values in SQL
-- 2. End each SQL command with a semicolon (;)
-- 3. SQL commands are not case-sensitive, but it's good practice to write them in CAPS
-- 4. The WHERE clause is used to filter records
-- 5. SELECT * means "select all columns" 