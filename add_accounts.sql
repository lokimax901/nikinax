-- Connect to the database
\c subman2

-- Add some test accounts
INSERT INTO accounts (email, password, status) VALUES
('john@example.com', 'password123', 'active'),
('alice@example.com', 'password456', 'active'),
('bob@example.com', 'password789', 'inactive');

-- Show all accounts
SELECT * FROM accounts;

-- Show only active accounts
SELECT email, created_at FROM accounts WHERE status = 'active';

-- Show only inactive accounts
SELECT email, created_at FROM accounts WHERE status = 'inactive'; 