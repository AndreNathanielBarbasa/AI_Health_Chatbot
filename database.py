import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check which database to use
DB_TYPE = os.getenv('DB_TYPE', 'mysql')  # Default to mysql for local

def get_db_connection():
    """Create and return a database connection"""
    
    if DB_TYPE == 'postgresql':
        # For Render (PostgreSQL)
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            connection = psycopg2.connect(
                os.getenv('DATABASE_URL'),
                cursor_factory=RealDictCursor
            )
            return connection
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None
    else:
        # For local development (MySQL)
        try:
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'health_chatbot_db')
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

def create_patient(first_name, last_name, age, sex, address, contact_number, medical_history):
    """Create a new patient record"""
    print(f"📊 Attempting to create patient: {first_name} {last_name}")
    
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to get database connection")
        return None
    
    try:
        cursor = connection.cursor()
        
        if DB_TYPE == 'postgresql':
            query = """
                INSERT INTO patients 
                (first_name, last_name, age, sex, address, contact_number, medical_history)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING patient_id
            """
            values = (first_name, last_name, age, sex, address, contact_number, medical_history)
            cursor.execute(query, values)
            patient_id = cursor.fetchone()['patient_id']
        else:
            query = """
                INSERT INTO patients 
                (first_name, last_name, age, sex, address, contact_number, medical_history)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (first_name, last_name, age, sex, address, contact_number, medical_history)
            cursor.execute(query, values)
            patient_id = cursor.lastrowid
            
        connection.commit()
        print(f"✅ Patient created with ID: {patient_id}")
        cursor.close()
        connection.close()
        return patient_id
    except Exception as e:
        print(f"❌ Error creating patient: {e}")
        return None

def get_patient(patient_id):
    """Get patient information by ID"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        if DB_TYPE == 'postgresql':
            cursor = connection.cursor()
        else:
            cursor = connection.cursor(dictionary=True)
            
        query = "SELECT * FROM patients WHERE patient_id = %s"
        cursor.execute(query, (patient_id,))
        patient = cursor.fetchone()
        cursor.close()
        connection.close()
        return patient
    except Exception as e:
        print(f"Error getting patient: {e}")
        return None

def create_chat_session(session_id, patient_id):
    """Create a new chat session"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = "INSERT INTO chat_sessions (session_id, patient_id) VALUES (%s, %s)"
        cursor.execute(query, (session_id, patient_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating chat session: {e}")
        return False

def save_message(session_id, role, content):
    """Save a chat message"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO chat_messages (session_id, role, content)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (session_id, role, content))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

def get_chat_history(session_id, limit=20):
    """Get chat history for a session"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        if DB_TYPE == 'postgresql':
            cursor = connection.cursor()
        else:
            cursor = connection.cursor(dictionary=True)
            
        query = """
            SELECT role, content, created_at 
            FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY created_at ASC
            LIMIT %s
        """
        cursor.execute(query, (session_id, limit))
        messages = cursor.fetchall()
        cursor.close()
        connection.close()
        return messages
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

def delete_chat_session(session_id):
    """Delete a chat session and its messages"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = "DELETE FROM chat_sessions WHERE session_id = %s"
        cursor.execute(query, (session_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting chat session: {e}")
        return False

def get_patient_sessions(patient_id):
    """Get all chat sessions for a patient"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        if DB_TYPE == 'postgresql':
            cursor = connection.cursor()
        else:
            cursor = connection.cursor(dictionary=True)
            
        query = """
            SELECT session_id, created_at 
            FROM chat_sessions 
            WHERE patient_id = %s 
            ORDER BY created_at DESC
        """
        cursor.execute(query, (patient_id,))
        sessions = cursor.fetchall()
        cursor.close()
        connection.close()
        return sessions
    except Exception as e:
        print(f"Error getting patient sessions: {e}")
        return []