import sqlite3
from sqlite3 import Error

def create_connection():
    """ create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect('prof/users.db')
    except Error as e:
        print(e)
    return conn

def select_all_users(conn):
    """
    Query all rows in the users table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return rows

def delete_user_by_username(conn, username):
    """
    Delete a user by username
    :param conn: the Connection object
    :param username: username of the user
    :return:
    """
    sql = 'DELETE FROM users WHERE username=?'
    cur = conn.cursor()
    cur.execute(sql, (username,))
    conn.commit()
    return cur.rowcount

def main():
    # create a database connection
    conn = create_connection()

    if conn is not None:
        while True:
            action = input("Enter 'view' to see all users, 'delete' to delete a user by username, or 'exit' to quit: ").strip().lower()
            if action == 'view':
                # query and display all users
                users = select_all_users(conn)
                if users:
                    print("Users:")
                    for user in users:
                        print(f"ID: {user[0]}, Username: {user[1]}, Nickname: {user[2]}, Password: {user[3]}, Emain: {user[4]}")
                else:
                    print("No users found.")
            elif action == 'delete':
                username = input("Enter the username of the user to delete: ").strip()
                deleted_count = delete_user_by_username(conn, username)
                if deleted_count > 0:
                    print(f"User '{username}' deleted successfully.")
                else:
                    print(f"User '{username}' not found.")
            elif action == 'exit':
                break
            else:
                print("Invalid action. Please enter 'view', 'delete', or 'exit'.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
