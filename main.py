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
            cursor.execute("""CREATE TABLE users
                            (UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                             UserName varchar(255) NOT NULL, 
                             UserPass varchar(255) NOT NULL)""") # maybe make password not null somewhen idk
            cursor.execute("""INSERT INTO users (UserName, UserPass)
                            VALUES ('testing', 'testing')""")
            
            cursor.execute("""CREATE TABLE artists
                            (ArtistID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            ArtistName varchar(255) NOT NULL,
                            DiscogsArtistID INTEGER NOT NULL)""")

            cursor.execute("""CREATE TABLE releases
                            (ReleaseID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            ReleaseName varchar(255) NOT NULL, 
                            ArtistID INTEGER NOT NULL,
                            DiscogsReleaseID INTEGER NOT NULL,
                            FOREIGN KEY(ArtistID) REFERENCES artists(ArtistID))""")
            # might need to get master id from discogs, may still call it DiscogsReleaseID in here for clarity though

            # need secondary user versions of releases and artists to deal with many to many relations
            cursor.execute("""CREATE TABLE user_artists
                            (recordID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER NOT NULL,
                            ArtistID INTEGER NOT NULL,
                            FOREIGN KEY(ArtistID) REFERENCES artists(ArtistID),
                            FOREIGN KEY(UserID) REFERENCES users(UserID))""")
            cursor.execute("""CREATE TABLE user_releases
                            (recordID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER NOT NULL,
                            ReleaseID INTEGER NOT NULL,
                            FOREIGN KEY(ReleaseID) REFERENCES releases(ReleaseID),
                            FOREIGN KEY(UserID) REFERENCES users(UserID))""")
            
            conn.commit

            # this also a very barebones silly return statement
            cursor.execute('SELECT * FROM users')
            result = cursor.fetchone()
            print(f'UserID: {result[0]}, Name: {result[1]}, Password: {result[2]}')


    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)
else:
    print("local database exists")


def add_to_db (table, field, value): # value here is the actual data we want to add
    try:
        with sqlite3.connect("MusicDB.db") as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            cursor = conn.cursor()
            # need to check if the value already exists first
            result = cursor.execute(f"""SELECT * FROM {table}
                                    WHERE {field}=?""",(value,)).fetchone()
            
            if result: # if a thing already exists
                print("value already exists")
            
            else: # if a thing doesn't exist
                cursor.execute(f"""INSERT INTO {table} ({field})
                                VALUES ('{value}')""") 
                print("added data successfully") # succes message for testing
                conn.commit


    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)

# test_table = urllib.parse.quote('users')
# test_field = urllib.parse.quote('UserName')
# test_value = urllib.parse.quote('slime')

# add_to_db(test_table, test_field, test_value)
