-- Connect to the database
\c subman2

-- Show all accounts to verify data persistence
SELECT 'Verifying data persistence - these accounts should still be here:' as message;
SELECT email, status, created_at FROM accounts; 