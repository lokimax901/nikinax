-- Connect to the database
\c subman2

-- Drop the existing table if it exists
DROP TABLE IF EXISTS accounts;

-- Create the accounts table with correct structure
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add some test accounts
INSERT INTO accounts (email, password, status) VALUES
('john@example.com', 'password123', 'active'),
('alice@example.com', 'password456', 'active'),
('bob@example.com', 'password789', 'inactive');

-- Show all accounts
SELECT 'Current accounts in database:' as message;
SELECT email, status, created_at FROM accounts;

-- Note: This data will remain in the database even after you close this window
-- or restart your computer. You can verify this by running this same query again later. 