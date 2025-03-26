# Setting up PostgreSQL on Windows

## Step 1: Download PostgreSQL
1. Go to the official PostgreSQL website: https://www.postgresql.org/download/windows/
2. Click on the "Download the installer" button
3. Choose the latest version (currently 16.x)
4. Select the Windows x86-64 installer

## Step 2: Install PostgreSQL
1. Run the downloaded installer
2. Click "Next" through the initial screens
3. Choose your installation directory (default is fine)
4. Select components to install:
   - ✓ PostgreSQL Server
   - ✓ pgAdmin 4 (GUI tool)
   - ✓ Command Line Tools
   - ✓ Stack Builder (optional)
5. Choose your data directory (default is fine)
6. Set a password for the database superuser (postgres)
   - Remember this password!
   - It's recommended to use a strong password
7. Keep the default port (5432)
8. Choose the default locale
9. Click "Install"

## Step 3: Verify Installation
1. Open Windows Start menu
2. Search for "pgAdmin 4" and open it
3. When prompted, enter the password you set during installation
4. You should see the PostgreSQL server in the left sidebar

## Step 4: Create Your First Database
1. In pgAdmin 4:
   - Right-click on "Databases"
   - Select "Create" → "Database"
   - Name it "accounts_db"
   - Click "Save"

## Step 5: Run the Schema
1. In pgAdmin 4:
   - Click on your new "accounts_db" database
   - Click the "Query Tool" button (looks like a document with a lightning bolt)
   - Copy and paste the contents of `schema.sql` into the query window
   - Click the "Execute/Refresh" button (looks like a play button)

## Step 6: Test the Database
1. In the same Query Tool:
   - Copy and paste the example queries from `guide.sql`
   - Try running them one by one to test the database

## Common Issues and Solutions
1. If you can't connect to the database:
   - Make sure PostgreSQL service is running
   - Check if you're using the correct password
   - Verify the port number (default is 5432)

2. If you get permission errors:
   - Make sure you're logged in as the postgres user
   - Check if you have the necessary privileges

## Next Steps
1. Learn to use pgAdmin 4 for visual database management
2. Try creating more tables and relationships
3. Practice writing SQL queries
4. Consider learning a programming language to interact with the database (Python, Node.js, etc.)

## Need Help?
- PostgreSQL documentation: https://www.postgresql.org/docs/
- pgAdmin documentation: https://www.pgadmin.org/docs/
- Stack Overflow: https://stackoverflow.com/questions/tagged/postgresql 