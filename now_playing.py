#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import tweepy
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
scope = 'user-read-currently-playing playlist-modify-public'
client_id = spotify_client_id
client_secret = spotify_client_secret
redirect_url = spotify_redirect_url
username = spotify_username
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_url)

poll_interval = 1

def main():
    last_id = 0
    while True:
        if token:
            sp = spotipy.Spotify(auth=token)
            results = sp.currently_playing()
            is_playing = results['is_playing']
            track_id = results['item']['id']

            if is_playing == True:
                if track_id != last_id:
                    track_name = results['item']['name']
                    artist_name = results['item']['artists'][0]['name']
                    cover_art = results['item']['album']['images'][0]['url']
                    track_preview = results['item']['external_urls']['spotify']
                    status_text = "#NowPlaying: " + track_name + " by " + artist_name + " " + track_preview
                    api.update_status(status_text)
                    print status_text
                    last_id = track_id
                    time.sleep(poll_interval)
                else:
                    time.sleep(poll_interval)
            else:
                last_id = 0
                time.sleep(poll_interval)
        else:
            print "Can't get token for", username
            sys.exit()

if __name__ == '__main__':
    sys.exit(main())
