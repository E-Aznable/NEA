# take an artist name and return their discogs ID and thumbnail address
# it should double-check if the artist is already in the table though

from dependencies import *
from urllib import *
import urllib.parse
import urllib.request

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
  response = urllib.request.urlopen(url)
  
  # Check if the request was successful
except urllib.error.URLError as e:
    print(e.reason)
  
# Parse the JSON response
data_response = response.read()
  
# Log or process the returned data
print("Discogs API response:", data_response)
  

# artist_id = data_response.results[0].id.toString()
# print(artist_id)

# image_url = data_response.results[0].cover_image
# print(image_url)
