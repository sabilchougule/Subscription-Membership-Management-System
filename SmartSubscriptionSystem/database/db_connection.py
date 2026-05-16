import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sabil414327",
        database="smart_subscription_system"
    )
    return connection