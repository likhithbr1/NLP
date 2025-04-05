# db_connection.py
import sys
import jaydebeapi

# Update these variables with your actual connection details.
JDBC_JAR = "/path/to/jconn3-6.0.jar"  # Path to your JDBC driver jar file
JDBC_URL = "jdbc:sybase:Tds:your_host:your_port/your_dbname"  # Replace with your host, port, dbname
JDBC_DRIVER = "com.sybase.jdbc3.jdbc.SybDriver"
DB_USER = "your_user"
DB_PASSWORD = "your_password"

def get_db_connection():
    """Establish and return a DB connection using jaydebeapi."""
    try:
        conn = jaydebeapi.connect(
            JDBC_DRIVER,
            JDBC_URL,
            [DB_USER, DB_PASSWORD],
            jars=JDBC_JAR
        )
        return conn
    except Exception as e:
        print(f"Error establishing DB connection: {e}")
        sys.exit(1)
