from database import get_db_connection, create_patient

# Test 1: Check database connection
print("Testing database connection...")
connection = get_db_connection()

if connection:
    print("✅ Database connection successful!")
    connection.close()
else:
    print("❌ Database connection failed!")
    print("Check your .env file and make sure XAMPP MySQL is running")
    exit()

