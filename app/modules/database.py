import mysql.connector
from mysql.connector import Error
from .config import Config

def get_db_connection():
    """اتصال به دیتابیس"""
    try:
        conn = mysql.connector.connect(**Config.DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ خطا در اتصال به دیتابیس: {e}")
        return None

def test_connection():
    """تست اتصال به دیتابیس"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return True
    return False

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """اجرای کوئری با مدیریت خودکار اتصال"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("اتصال به دیتابیس برقرار نشد")
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        if commit:
            conn.commit()
            
        return result
        
    except Exception as e:
        print(f"❌ خطا در اجرای کوئری: {e}")
        if conn and commit:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()