from database import get_db_connection, DB_TYPE

def init_database():
    """Initialize database tables if they don't exist"""
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create patients table
        if DB_TYPE == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    age INTEGER NOT NULL,
                    sex VARCHAR(10) NOT NULL,
                    address TEXT,
                    contact_number VARCHAR(20),
                    medical_history TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    sex VARCHAR(10) NOT NULL,
                    address TEXT,
                    contact_number VARCHAR(20),
                    medical_history TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Create chat_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id VARCHAR(100) PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create chat_messages table
        if DB_TYPE == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Database tables initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database()