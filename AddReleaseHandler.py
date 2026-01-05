# this file is a combination of the old GetArtistID, GetReleaseID and LinkTracksToRelease files, and does everything they do in one fell swoop
# takes an input artist name and release name to find necessary data and create database entries for the releas

import urllib.parse
import urllib.request
import json
import urllib.parse
import urllib.request
import sqlite3

# may need to make seperate functions that only add an artist
# or a release, which must be linked to an existing artist
def AddArtist(artist_name, user_id): # artist func
    # need to take an input from another file
    encoded_artist = urllib.parse.quote(artist_name)

    # Construct the Discogs API URL using consumer key and secret for authentication
    # don't worry that url 2 is first it's fine
    url = f"https://api.discogs.com/database/search?q={encoded_artist}&type=artist&key=xrSbUFUOiFdlCrxyqXLH&secret=kSEmEHQSYwBTmKrUuZXfloXAMdVqWmwx"

    try:
        # Make the HTTP request
        data_response = json.load(urllib.request.urlopen(url))
        # could be nicer to separate the request and variable assignment, but we're saving a single line of code here so
        # Check if the request was successful
    except urllib.error.URLError as e:
        print(e.reason)

    # retrieve data from parsed response
    # don't worry about that warning it'll never matter
    artist_id = data_response["results"][0]["id"]
    print(f"artist ID: {artist_id}")

    artist_image_url = data_response["results"][0]["cover_image"]
    print(f"artist image url: {artist_image_url}")

    # make database entries to correct user tables
    try:
        with sqlite3.connect("MusicDB.db") as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            cursor = conn.cursor()
            # first check if this stuff is already in the table and break if so
            result = cursor.execute(f"""SELECT DiscogsArtistID
                            FROM artists
                            WHERE DiscogsArtistID = ?""", (artist_id,)).fetchone()
            if result:  # if the data is already there, then just say so and don't add
                print("value already exists")
                return False
            else: # if data isn't there, add it
                cursor.execute(f"""INSERT INTO artists (ArtistName, DiscogsArtistID, ArtistImage)
                                VALUES ('{artist_name}', {artist_id}, '{artist_image_url}')""")
                conn.commit()
                print("data added successfully!")
                return True
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)


def Addrelease(release_name, artist_name, user_id): # release + tracks func
    encoded_artist = urllib.parse.quote(artist_name)
    encoded_release = urllib.parse.quote(release_name)

    url = f"https://api.discogs.com/database/search?q={encoded_release}&type=master&artist={encoded_artist}&key=xrSbUFUOiFdlCrxyqXLH&secret=kSEmEHQSYwBTmKrUuZXfloXAMdVqWmwx"

    try:
        data_response = json.load(urllib.request.urlopen(url))
    except urllib.error.URLError as e:
        print(e.reason)

    master_id = data_response["results"][0]["master_id"]
    print(f"release master ID: {master_id}")

    release_image_url = data_response["results"][0]["cover_image"]
    print(f"release image url: {release_image_url}")
    # this whole way of searching is only mostly accurate, I don't think there's a way to make it better either

    # find tracks now
    tracks_url = f"https://api.discogs.com/masters/{master_id}"
    try:
        tracks_data_response = json.load(urllib.request.urlopen(tracks_url))
    except urllib.error.URLError as e:
        print("urllib error:", e)

    print("Discogs API response - tracklist:", tracks_data_response)

    tracklist = []
    for i in range(len(tracks_data_response["tracklist"])):
        tracklist.append(tracks_data_response["tracklist"][i]["title"])
    print(f"tracklist: {tracklist}")

    try:
        with sqlite3.connect("MusicDB.db") as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            cursor = conn.cursor()
            # check if this stuff already exists too
            result = cursor.execute(f"""SELECT DiscogsReleaseID
                                        FROM releases
                                        WHERE DiscogsReleaseID = ?""", (master_id,)).fetchone()
            if result:  # if the data is already there, then just say so and don't add
                print("value already exists")
                return False
            else:  # if data isn't there, add it
                cursor.execute(f"""SELECT ArtistID
                                                FROM artists
                                                WHERE ArtistName = '{artist_name}'""")
                artist_id_result_tuple = cursor.fetchone()
                artist_id_result = artist_id_result_tuple[0]
                cursor.execute(f"""INSERT INTO releases (ReleaseName, ArtistID, DiscogsReleaseID, ReleaseImage)
                                                VALUES ('{release_name}', {artist_id_result}, {master_id}, '{release_image_url}')""")

                cursor.execute(f"""INSERT INTO user_artists (UserID, ArtistID)
                                                VALUES ({user_id}, {artist_id_result})""")

                cursor.execute(f"""SELECT ReleaseID
                                                FROM releases
                                                WHERE DiscogsReleaseID = '{master_id}'""")
                release_id_result_tuple = cursor.fetchone()
                release_id_result = release_id_result_tuple[0]
                cursor.execute(f"""INSERT INTO user_releases (UserID, ReleaseID)
                                                VALUES ({user_id}, {release_id_result})""")

                for i in range(len(tracklist)):
                    cursor.execute(f"""INSERT INTO tracks 
                                                (TrackName, TrackNum, ReleaseID)
                                                VALUES ('{tracklist[i]}', {i+1}, {release_id_result})""")
                    i+=1

    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)


def AddBoth(artist_name, release_name, user_id): # very simple to do both at once lol
    AddArtist(artist_name, user_id)
    Addrelease(release_name, artist_name, user_id)

