import getpass
import mysql.connector

pwd = getpass.getpass("Please enter the password for the 'pocuser' account: ")

try:
    # 1. Establish the connection
    connection = mysql.connector.connect(
        host="apps.marble.ccs.ornl.gov",
        port=30306, # Specify your port number here (e.g., 3306 or a custom port)
        database="pocdb",
        user="pocuser",
        password=pwd
    )

    if connection.is_connected():
        print("Successfully connected to the database!")

        # 2. Create a cursor object to execute SQL statements
        cursor = connection.cursor()

        # 3. Execute a basic SQL query
        cursor.execute("SELECT * FROM persistence_test;")

        # 4. Fetch and print the records
        records = cursor.fetchall()
        for row in records:
            print(row)

except Error as e:
    print(f"Error while connecting to MySQL: {e}")

finally:
    # 5. Always close the cursor and connection when done
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")