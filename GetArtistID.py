# take an artist name and return their discogs ID and thumbnail address
# it should double-check if the artist is already in the table though

import urllib.parse
import urllib.request
import json

data_response = []

# need to take an input from another file
artist_name = "castle rat" # placeholder
encoded = urllib.parse.quote(artist_name)
print(encoded)

# this is not very important but it's nice
user_agent = "personal music manager"

# Construct the API URL
# Construct the Discogs API URL using consumer key and secret for authentication
url = f"https://api.discogs.com/database/search?q={encoded}&type=artist&key=xrSbUFUOiFdlCrxyqXLH&secret=kSEmEHQSYwBTmKrUuZXfloXAMdVqWmwx"

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
artist_id = data_response["results"][0]["id"]
print(artist_id)

image_url = data_response["results"][0]["cover_image"]
print(image_url)
