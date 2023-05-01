import spotipy
import spotipy.util as util
import tweepy
import urllib.request
import time
import os

# Set up Twitter API credentials
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Set up Spotify API credentials
spotify_username = 'YOUR_SPOTIFY_USERNAME'
scope = 'user-read-currently-playing'
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
redirect_uri = 'http://localhost:8080/callback'

# Authenticate with Spotify API
token = util.prompt_for_user_token(spotify_username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
sp = spotipy.Spotify(auth=token)

# Create function to get currently playing track
def get_current_track():
    track = sp.current_user_playing_track()
    if track is None:
        return None
    else:
        track_name = track['item']['name']
        artists = [artist['name'] for artist in track['item']['artists']]
        artist_names = ', '.join(artists)
        track_uri = track['item']['external_urls']['spotify']
        image_url = track['item']['album']['images'][0]['url']
        return track_name, artist_names, track_uri, image_url

# Create function to send tweet and update profile picture and cover photo
def send_tweet(track_name, artist_names, track_uri, image_url):
    # Download image to local file
    urllib.request.urlretrieve(image_url, 'album_artwork.jpg')
    # Update profile picture
    api.update_profile_image('album_artwork.jpg')
    # Update cover photo
    api.update_profile_banner('album_artwork.jpg')
    # Send tweet
    tweet_text = f"#NowPlaying: {track_name} by {artist_names}\n{track_uri}"
    api.update_status(tweet_text)

# Get initial track
current_track = None

# Create loop to continuously check for updates and send tweets
while True:
    time.sleep(10) # Wait 10 seconds between each check
    new_track = get_current_track()
    if new_track is not None and new_track != current_track:
        track_name, artist_names, track_uri, image_url = new_track
        send_tweet(track_name, artist_names, track_uri, image_url)
        current_track = new_track