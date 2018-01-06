#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import tweepy
import pprint
import spotipy
import spotipy.util as util
import json
from keys import *

# Twitter https://apps.twitter.com/
consumer_key = twitter_consumer_key
consumer_secret = twitter_consumer_secret
access_key = twitter_access_key
access_secret = twitter_access_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# Spotify https://developer.spotify.com/my-applications/
scope = 'playlist-modify-public'
client_id = spotify_client_id
client_secret = spotify_client_secret
redirect_url = spotify_redirect_url
username = spotify_username
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_url)


while True:
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_playlists()
        playlist_name = results['items'][0]['name']
        playlist_uri = results['items'][0]['uri']

        print playlist_name
        print(playlist_uri)
        #data = results
        #with open('data.json', 'w') as outfile:
        #    json.dump(data, outfile)
