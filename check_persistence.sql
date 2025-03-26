-- Connect to the database
\c subman2

-- First, let's see what accounts we currently have
SELECT 'Current accounts in database:' as message;
SELECT email, status, created_at FROM accounts;

-- Add a new test account
INSERT INTO accounts (email, password, status)
VALUES ('test_persistence@example.com', 'test123', 'active');

-- Show the new account was added
SELECT 'After adding new account:' as message;
SELECT email, status, created_at FROM accounts;

-- Note: This data will remain in the database even after you close this window
-- or restart your computer. You can verify this by running this same query again later. 