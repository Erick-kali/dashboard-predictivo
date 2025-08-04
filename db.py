def get_connection():
    import mysql.connector
    from mysql.connector import Error
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='sin_sentido'
        )
        return conn
    except Error as e:
        print(f"Error conectando a BD: {e}")
        return None