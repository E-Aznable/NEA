# main
# runs other files
# creates tables if none present

import urllib.parse
import urllib.request
import json
import sqlite3
import os.path

exists_check = os.path.isfile("MusicDB.db")
if not exists_check:
    print("no local database")
    try:
        with sqlite3.connect("MusicDB.db") as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            # this is just placeholder to add a value, it doesn't like to be run when there is already a table
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE users (UserID INTEGER PRIMARY KEY AUTOINCREMENT, UserName varchar(255) NOT NULL)')
            cursor.execute("INSERT INTO users (UserName) VALUES ('Harper')") 
            conn.commit

            #this also a very barebones silly return statement
            cursor.execute('SELECT * FROM users')
            result = cursor.fetchone()
            print(f'UserID: {result[0]}, Name: {result[1]}')


    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)
else:
    print("local database exists")
