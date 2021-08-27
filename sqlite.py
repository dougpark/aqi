# sqlite 3 with python
# August 2021
# today is the day
# now is the time yes!

import sqlite3

db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
cursor = db.cursor()

print("Opened database successfully!")

# cursor = cursor.cursor()

try:
    cursor.execute('''CREATE TABLE IF NOT EXISTS company
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         AGE            INT     NOT NULL,
         ADDRESS        CHAR(50),
         SALARY         REAL);''')
    print("Table created successfully")
except Exception as e:
    print("Table already exists: ", e)

try:
    cursor.execute("INSERT INTO company (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (1, 'Paul', 32, 'California', 20000.00 )")

    cursor.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (2, 'Allen', 25, 'Texas', 15000.00 )")

    cursor.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )")

    cursor.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )")

    db.commit()
    print("Records created successfully")
except Exception as e:
    print("Records already exist: ", e)

keys = ('2',)
cursor.execute(
    "SELECT id, name, address, salary FROM company WHERE id >= ?", keys)
rows = cursor.fetchall()

for row in rows:
    print(row.keys())
    print(tuple(row))

    print("ID = ", row['id'])
    print("NAME = ", row[1])  # alternate access
    print("ADDRESS = ", row['address'])
    print("SALARY = ", row['salary'], "\n")

print("Operation done successfully")

db.close()
