# this takes an album name and artist name to give us a release ID and other useful stuff

import urllib.parse
import urllib.request
import json

data_response = []

# need to take an input from another file
artist_name = "pink floyd"  # placeholder
encoded_artist = urllib.parse.quote(artist_name)
print(encoded_artist)

release_name = "dark side of the moon" # placeholder
encoded_release = urllib.parse.quote(release_name)

# this is not very important but it's nice
user_agent = "personal music manager"

# Construct the API URL
# Construct the Discogs API URL using consumer key and secret for authentication
url = f"https://api.discogs.com/database/search?q={encoded_release}&type=master&artist={encoded_artist}&key=xrSbUFUOiFdlCrxyqXLH&secret=kSEmEHQSYwBTmKrUuZXfloXAMdVqWmwx"

try:
    # Make the HTTP request to the Discogs API
    data_response = json.load(urllib.request.urlopen(url))
    # could be nicer to separate the request and variable assignment, but we're saving a single line of code here so

    # Check if the request was successful
except urllib.error.URLError as e:
    print(e.reason)

# Parse the JSON response
# up there now

# Log or process the returned data
print("Discogs API response:", data_response)

# retrieve data from parsed response
# don't worry about that warning it'll never matter
master_id = data_response["results"][0]["master_id"]
print(master_id)

cover_image_url = data_response["results"][0]["cover_image"]
print(cover_image_url)
# this whole way of searching is only mostly accurate, I don't think if there's a way to make it better either