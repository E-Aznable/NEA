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
    print("no local database, creating now")
    try:
        with sqlite3.connect("MusicDB.db") as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            # this is just placeholder to add a value, it doesn't like to be run when there is already a table
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE users
                            (UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                             UserName varchar(255) NOT NULL, 
                             UserPass varchar(255) NOT NULL)""")
            cursor.execute("""INSERT INTO users (UserName, UserPass)
                            VALUES ('testing', 'testing')""")
            
            cursor.execute("""CREATE TABLE artists
                            (ArtistID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            ArtistName varchar(255) NOT NULL,
                            DiscogsArtistID INTEGER NOT NULL,
                            ArtistImage varchar(255))""")
            cursor.execute("""INSERT INTO artists (ArtistName, DiscogsArtistID, ArtistImage)
                            VALUES ('pink floyd', 45467, 'https://i.discogs.com/L3xODvccXCrOv8yQ717EIfcw52brkl4GlTv6rkGVAXo/rs:fit/g:sm/q:90/h:397/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9BLTQ1NDY3/LTE0MDU1OTMzMDIt/ODYzMy5qcGVn.jpeg')""") # placeholder

            cursor.execute("""CREATE TABLE releases
                            (ReleaseID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            ReleaseName varchar(255) NOT NULL,
                            ReleaseImage varchar(255),
                            ArtistID INTEGER NOT NULL,
                            DiscogsReleaseID INTEGER NOT NULL,
                            FOREIGN KEY(ArtistID) REFERENCES artists(ArtistID))""")
            # might need to get master id from discogs, may still call it DiscogsReleaseID in here for clarity though
            cursor.execute("""INSERT INTO releases (ReleaseName, ArtistID, DiscogsReleaseID, ReleaseImage)
                            VALUES ('dark side of the moon', 1, 10362, 'https://i.discogs.com/oHPDj8NWtkGhq7kSCJuJ4pEnThoYx3JgU9kcDyvbeKo/rs:fit/g:sm/q:90/h:609/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTE4NzMw/MTMtMTcyNzc2NDkx/OS04NTI3LmpwZWc.jpeg')""") # placeholder

            # need secondary user versions of releases and artists to deal with many to many relations
            cursor.execute("""CREATE TABLE user_artists
                            (user_artistID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER NOT NULL,
                            ArtistID INTEGER NOT NULL,
                            FOREIGN KEY(ArtistID) REFERENCES artists(ArtistID),
                            FOREIGN KEY(UserID) REFERENCES users(UserID))""")
            cursor.execute("""INSERT INTO user_artists (UserID, ArtistID)
                            VALUES (1, 1)""") # placeholder
            cursor.execute("""CREATE TABLE user_releases
                            (user_releaseID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER NOT NULL,
                            ReleaseID INTEGER NOT NULL,
                            FOREIGN KEY(ReleaseID) REFERENCES releases(ReleaseID),
                            FOREIGN KEY(UserID) REFERENCES users(UserID))""")
            cursor.execute("""INSERT INTO user_releases (UserID, ReleaseID)
                            VALUES (1, 1)""")

            conn.commit()

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
