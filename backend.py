# called calling this backend now because it seems sensible
# should ALWAYS run before anything else, creates the database


# HUGE apologies for my mixing of camelcase and whatever the other one is called, it is unlikely I will fix this


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
                            ArtistImage varchar(255) NOT NULL)""")
            cursor.execute("""INSERT INTO artists (ArtistName, DiscogsArtistID, ArtistImage)
                            VALUES ('FAKE pink floyd', 694204546769420, 'https://i.discogs.com/L3xODvccXCrOv8yQ717EIfcw52brkl4GlTv6rkGVAXo/rs:fit/g:sm/q:90/h:397/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9BLTQ1NDY3/LTE0MDU1OTMzMDIt/ODYzMy5qcGVn.jpeg')""") # placeholder

            cursor.execute("""CREATE TABLE releases
                            (ReleaseID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            ReleaseName varchar(255) NOT NULL,
                            ReleaseImage varchar(255) NOT NULL,
                            ArtistID INTEGER NOT NULL,
                            DiscogsReleaseID INTEGER NOT NULL,
                            FOREIGN KEY(ArtistID) REFERENCES artists(ArtistID))""")
            # might need to get master id from discogs, may still call it DiscogsReleaseID in here for clarity though
            cursor.execute("""INSERT INTO releases (ReleaseName, ArtistID, DiscogsReleaseID, ReleaseImage)
                            VALUES ('FAKE dark side of the moon', 1, 694201036269420, 'https://i.discogs.com/oHPDj8NWtkGhq7kSCJuJ4pEnThoYx3JgU9kcDyvbeKo/rs:fit/g:sm/q:90/h:609/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTE4NzMw/MTMtMTcyNzc2NDkx/OS04NTI3LmpwZWc.jpeg')""") # placeholder

            # need secondary user versions of releases and artists to deal with many-to-many relations
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

            # tracks table for tracks duh
            cursor.execute("""CREATE TABLE tracks
                            (TrackID INTEGER PRIMARY KEY AUTOINCREMENT,
                            TrackName varchar(255) NOT NULL,
                            TrackNum INTEGER,
                            ReleaseID INTEGER,
                            FOREIGN KEY(ReleaseID) REFERENCES releases(ReleaseID))""")
            cursor.execute("""INSERT INTO tracks (TrackName, TrackNum, ReleaseID)
                            VALUES ('FAKE eclipse', 10, 1)""")

            conn.commit()

            # return statement test
            cursor.execute('SELECT * FROM users')
            result = cursor.fetchone()
            print(f'UserID: {result[0]}, Name: {result[1]}, Password: {result[2]}')


    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)
else:
    print("local database exists")


# this function is useful in theory but i had to make a whole file just for handling new data with particulars to the database stuff
# so the databse is added to from there insead
# meaning this func is kind of useless now and would be a lot of effort to make useful
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
                return False # if I end up using this, returning a boolean will be very helpful
            
            else: # if a thing doesn't exist
                cursor.execute(f"""INSERT INTO {table} ({field})
                                VALUES ('{value}')""") 
                print("added data successfully") # success message for testing
                conn.commit
                return True


    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)


# replace_in_db
# and
# remove_from_db
# could both be useful functions maybe