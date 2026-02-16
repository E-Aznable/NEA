# takes an input artist name and release name to find necessary data and create database entries for the releas

import urllib.parse
import urllib.request
import json
import urllib.parse
import urllib.request
import sqlite3


def AddArtist(artist_name, user_id):  # artist func
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
            result = cursor.execute(
                "SELECT ArtistID FROM artists WHERE DiscogsArtistID = ?",
                (artist_id,)
            ).fetchone()
            if result:  # if the data is already there, then just say so and don't add
                print("value already exists")
                return False
            else:
                cursor.execute(
                    """
                    INSERT INTO artists (ArtistName, DiscogsArtistID, ArtistImage)
                    VALUES (?, ?, ?)
                    """,
                    (artist_name, artist_id, artist_image_url)
                )

                artist_id = cursor.execute(
                    "SELECT ArtistID FROM artists WHERE DiscogsArtistID = ?",
                    (artist_id,)
                ).fetchone()[0]

                # link artist to user (ignore if already linked)
            cursor.execute(
                """
                INSERT OR IGNORE INTO user_artists (UserID, ArtistID)
                VALUES (?, ?)
                """,
                (user_id, artist_id)
            )

            conn.commit()
            return artist_id

    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)
        return False


def AddRelease(artist_name, release_name, user_id):  # release + tracks func
    AddArtist(artist_name, user_id)  # wow I made my life so easy
    # this basically works?? crazy

    release_name = release_name
    artist_name = artist_name

    encoded_artist = urllib.parse.quote(artist_name)
    encoded_release = urllib.parse.quote(release_name)

    url = f"https://api.discogs.com/database/search?q={encoded_release}&type=master&artist={encoded_artist}&key=xrSbUFUOiFdlCrxyqXLH&secret=kSEmEHQSYwBTmKrUuZXfloXAMdVqWmwx"

    try:
        data_response = json.load(urllib.request.urlopen(url))
    except urllib.error.URLError as e:
        print(e.reason)
        return (e.reason)

    print(data_response)

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

    # print("Discogs API response - tracklist:", tracks_data_response)

    tracklist = []
    for i in range(len(tracks_data_response["tracklist"])):
        tracklist.append(tracks_data_response["tracklist"][i]["title"])
    print(f"tracklist: {tracklist}")

    try:
        with sqlite3.connect("MusicDB.db") as conn:
            cursor = conn.cursor()

            # check if release already exists
            existing = cursor.execute(
                "SELECT ReleaseID FROM releases WHERE DiscogsReleaseID = ?",
                (master_id,)
            ).fetchone()

            if existing:
                release_id = existing[0]
            else:
                artist_row = cursor.execute(
                    "SELECT ArtistID FROM artists WHERE ArtistName = ?",
                    (artist_name,)
                ).fetchone()

                if not artist_row:
                    print("Artist not found after insertion")
                    return False

                artist_id = artist_row[0]

                cursor.execute(
                    """
                    INSERT INTO releases
                        (ReleaseName, ArtistID, DiscogsReleaseID, ReleaseImage)
                    VALUES (?, ?, ?, ?)
                    """,
                    (release_name, artist_id, master_id, release_image_url)
                )

                release_id = cursor.execute(
                    "SELECT ReleaseID FROM releases WHERE DiscogsReleaseID = ?",
                    (master_id,)
                ).fetchone()[0]

                # link release to user
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO user_releases (UserID, ReleaseID)
                    VALUES (?, ?)
                    """,
                    (user_id, release_id)
                )

                # insert tracks safely
                for track_num, track_name in enumerate(tracklist, start=1):
                    cursor.execute(
                        """
                        INSERT INTO tracks (TrackName, TrackNum, ReleaseID)
                        VALUES (?, ?, ?)
                        """,
                        (track_name, track_num, release_id)
                    )

            conn.commit()
            return True

    except sqlite3.Error as e:
        print("SQLite error (AddRelease):", e)
        return False


def AddNew(artist_id, artist_name, user_id): # take artist name because we can do that way easier before rather than querying db to get it
    # DO THIS
    user_id = user_id
    artist_id = artist_id
    artist_name = artist_name
    url = f"https://api.discogs.com/artists/{artist_id}/releases?sort=year&sort_order=desc"

    try:
        data_response = json.load(urllib.request.urlopen(url))
    except urllib.error.URLError as e:
        print(e.reason)
        return e.reason

    print(data_response)

    latest_discog_id = data_response["releases"][0]["id"]
    print(f"latest discog ID: {latest_discog_id}")

    latest_release_name = data_response["releases"][0]["title"]
    print(f"latest release name: {latest_release_name}")

    try:
        main_release_id = data_response["releases"][0]["main_release"]
        print(f"main release ID: {main_release_id}")
    except:
        # discogs list things like physical releases and promo merch
        # we only want album masters
        # loop through to make sure all fields are there and correct
        i = 1
        for i in range(len(data_response["releases"])):
            print(f"try {i}")
            if 'main_release' in data_response["releases"][i]:
                main_release_id = str(data_response["releases"][i]["main_release"])
                print(f"main release ID: {main_release_id}")

                latest_discog_id = data_response["releases"][i]["id"]
                print(f"latest discog ID: {latest_discog_id}")

                latest_release_name = data_response["releases"][i]["title"]
                print(f"latest release name: {latest_release_name}")

                AddRelease(artist_name, latest_release_name, user_id)
                return True # like this?
    else:
        print("SUCCESS: should be all good")
        AddRelease(artist_name, latest_release_name, user_id)
        return True



def AddBoth(artist_name, release_name, user_id):  # very simple to do both at once lol
    AddArtist(artist_name, user_id)
    AddRelease(artist_name, release_name, user_id)
