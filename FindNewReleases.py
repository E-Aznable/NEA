# find new releases using an artist id (requires artist name to find id)
# will be on a page where all artists are displayed, and you can tick them as followed
# checks if the found releases are already in your database, and if not, add them

import urllib.parse
import urllib.request
import json

data_response = []

# needs multiple inputs
release_ID_list = [3966044] # placeholder
artist_ID = 13121262 # placeholder
print(f'artist id {artist_ID} and release id list {release_ID_list[0]}')

# key and secret aren't need (and apparently break it?) &key=xrSbUFUOiFdlCrxyqXLH&secret=kSEmEHQSYwBTmKrUuZXfloXAMdVqWmwx
url = f"https://api.discogs.com/artists/{artist_ID}/releases?sort=year&sort_order=desc"

try:
    # Make the HTTP request to the Discogs API
    data_response = json.load(urllib.request.urlopen(url))
  
    # Check if the request was successful
except urllib.error.URLError as e:
    print(e.reason)

#parsed json up there
  
# Log or process the returned data
print("Discogs API response:", data_response)
  
# retrieve data from parsed response
# don't worry about that warning it'll never matter
latest_discog_id = data_response["releases"][0]["id"]
print(latest_discog_id)

latest_release_name = (data_response["releases"][0]["title"]).lower()
print(latest_release_name)

artist_name = (data_response["releases"][0]["artist"]).lower()
print(artist_name)

main_release_id = data_response["releases"][0]["main_release"]
print(main_release_id)

# discogs list things like physical releases and promo merch
# we only want album masters
# loop through to make sure all fields are there and correct

i = 1
if (main_release_id == None):
    for i in range(len(data_response["releases"])):
        print(f"try {i}")
        if ('main_release' in data_response["releases"][i]):
            main_release_id = str(data_response["releases"][i]["main_release"])

        latest_discog_id = str(data_response["releases"][i]["id"])
        print(latest_discogs_id)

        latest_release_name = (data_response["releases"][i]["title"]).lower()
        print(latst_release_name)
        break
else:
    print("SUCCESS: should be all good")
