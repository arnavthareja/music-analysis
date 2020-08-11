# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Spotify API Data Collection  
# 
# ### In this notebook, we will fetch music data from the Spotify API using the spotipy library  
# 
# The Spotify API allows us to collect data about music on Spotify, including metadata and music features  
# Searching for music will give us songs that are currently popular or have recently been popular  
# It is important to note that searching for old tracks will not give the tracks that were popular at that time, but tracks made at that time that are popular now  
# To find tracks that were popular in earlier years, it would likely be easier to use Billboard charts for the desired timeframe

# %%
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests

# %% [markdown]
# This will create an instance of spotipy with the Spotify Developer Account Credentials  
# The Spotify Developer ID and Secret are stored in environment variables on the system

# %%
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# %% [markdown]
# ## Data Collection
# 
# We will store the names of features we want to collect in a list and create dictionaries to temporarily hold the data  
# The metadata and analysis lists and dictionaries are separated to make inserting data easier, as the data is gathered in two separate steps

# %%
features_list = ['artist', 'name', 'id', 'release_date', 'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']
metadata_list = features_list[:5]
analysis_list = features_list[5:]

features = {feature : [] for feature in features_list}
metadata = {feature : features[feature] for feature in metadata_list}
analysis = {feature : features[feature] for feature in analysis_list}

# %% [markdown]
# We will be looking at 2000 different songs from 2018 to 2020, as the Spotify API only allows searches to access the first 2000 results  
# Data is gathered in increments of 50, the maximum allowed by the Spotify API

# %%
start_year = 2018
end_year = 2020
search_limit = 50
num_tracks = 2000

#for year in range(start_year, end_year + 1):
for i in range(0, num_tracks, search_limit):
    print("\r", "iteration {}".format(i // search_limit), end="")
    current_tracks = []
    try:
        results = sp.search(q='year:{}-{}'.format(start_year, end_year), limit=search_limit, type='track', offset=i)
    except (requests.HTTPError, spotipy.SpotifyException):
        pass
    for j, t in enumerate(results['tracks']['items']):
        current_tracks.append(t['id'])
        for k, v in metadata.items():
            if k == 'artist':
                v.append(t['artists'][0]['name'])
            elif k == 'release_date':
                v.append(t['album'][k])
            else:
                v.append(t[k])
    try:
        feature_results = sp.audio_features(current_tracks)
    except (requests.HTTPError, spotipy.SpotifyException):
        pass
    for feature in feature_results:
        for k, v in analysis.items():
            v.append(feature[k])

# %% [markdown]
# ## Data Storage
# 
# Once the dictionaries are filled, the data will be moved to a pandas dataframe for more features and easier analysis  
# The songs are sorted by popularity to see which songs are currently the most popular  
# 
# Some songs have a popularity of 0, which is a result of Spotify's popularity algorithm likely only taking recent streaming data into account  
# Old songs with a popularity of 0 may have been popular earlier, but they aren't streamed as much anymore  
# Some songs are too new to have a popularity value yet, so they also have a popularity of 0  
# 
# We will filter out songs with popularity 0 and new songs  
# As of August 10, 2020, a new song is defined as one that was released on or after August 1, 2020

# %%
df = pd.DataFrame(features)
# Filter out songs with popularity 0 and very new songs
df = df[(df.popularity != 0) & (df.release_date < '2020-08-01')].sort_values(by='popularity', ascending=False).reset_index(drop=True)
df

# %% [markdown]
# After filtering, the lowest popularity value is 39, so there is a mix of popular and semi-popular songs, but not unpopular songs  
# This dataset is not ideal to see what differentiates popular songs from unpopular ones, but hopefully it will still tell us about characteristics of popular songs and what makes them more successful than semi-popular songs

# %%
print(min(df.popularity))

# %% [markdown]
# We will store our collected data in a csv file for later use

# %%
df.to_csv('..\data\spotify.csv',index=False)

# %% [markdown]
# And we're done.

