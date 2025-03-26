-- Connect to the existing database
\c subman2

-- Check if the accounts table exists and show its structure
\d accounts

-- Show all existing accounts
SELECT * FROM accounts;

-- Add a new test account
INSERT INTO accounts (email, password_hash, status)
VALUES ('newuser@example.com', 'hashed_password_here', 'active');

-- Show all accounts again to verify the new account was added
SELECT * FROM accounts;

-- Try to find a specific account by email
SELECT * FROM accounts WHERE email = 'newuser@example.com';

-- Update an account's status
UPDATE accounts 
SET status = 'active' 
WHERE email = 'newuser@example.com';

-- Show the updated account
SELECT * FROM accounts WHERE email = 'newuser@example.com'; 