from werkzeug.security import generate_password_hash
import mysql.connector

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="forum"
)
cur = db.cursor()

for username, pw in [("holros", "foo"), ("manfol", "bar"), ("goskor", "baz")]:
    cur.execute(
        "UPDATE users SET password = %s WHERE username = %s",
        (generate_password_hash(pw), username)
    )

db.commit()
cur.close()
db.close()
print("Klart")