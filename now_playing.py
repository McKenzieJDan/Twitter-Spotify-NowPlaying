#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import datetime
import urllib
import requests
import json
import sqlite3
import tweepy
import spotipy
import spotipy.util as util
from PIL import Image
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
scope = 'user-read-currently-playing playlist-modify-public playlist-modify-private'
client_id = spotify_client_id
client_secret = spotify_client_secret
redirect_url = spotify_redirect_url
username = spotify_username
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_url)

sp = spotipy.Spotify(auth=token)
poll_interval = 20

def get_new_token():
    token = util.prompt_for_user_token(username, scope, client_id=client_id,client_secret=client_secret,redirect_uri=redirect_url)
    print("Token",token)
    #file = open("token.txt","w")
    file.write(token)
    file.close()

def do_token_refresh():
    while(True):
      get_new_token()
      time.sleep(1000)

def getCurrentlyPlaying():
    results = sp.currently_playing()

    is_playing = results['is_playing']
    currently_playing = results['item']

    return is_playing, currently_playing

def updateTwitter(track):
    tweet_text = "#NowPlaying: " + track['name'] + " by " + track['artists'][0]['name'] + " " + track['external_urls']['spotify']
    cover_art = track['album']['images'][0]['url']
    urllib.urlretrieve(cover_art, "profile_image.jpg")
    profile_image = 'profile_image.jpg'

    try:
        api.update_status(tweet_text)
        api.update_profile_image(profile_image)
        api.update_profile_banner(profile_image)
        update = True
    except tweepy.error.TweepError:
        update = False

    return update

def updateSpotifyPlaylist(track):
    playlist_id = spotify_playlist
    sp.user_playlist_add_tracks(username, playlist_id, [track['uri']], position=0)
    return

def updateDatabase(track):
    try:
        sqlite_file = 'now_playing.db'
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()

        name = str(track['name'])
        c.execute('SELECT 1 FROM nowplaying WHERE track=? LIMIT 1', (name,))
        name_exists = c.fetchone() is not None

        if not name_exists:
            c.execute("INSERT OR IGNORE INTO nowplaying (track, artist, album, totalPlays, firstListen) VALUES ('{a1}', '{a2}', '{a3}', 1, datetime('now'))".\
                      format(a1=track['name'], a2=track['artists'][0]['name'], a3=track['album']['name']))
        else:
            c.execute("UPDATE nowplaying SET totalPlays = totalPlays + 1 WHERE track = '{a1}'".\
                      format(a1=track['name']))
            c.execute("UPDATE nowplaying SET lastListen = datetime('now') WHERE track = '{a1}'".\
                      format(a1=track['name']))

        conn.commit()
        conn.close()

    except sqlite3.Error as er:
        print 'er:', er.message

    return

def update(last_id):

    # Get currently playing from spotify
    is_playing, track = getCurrentlyPlaying()

    # No track playing so return with id=0
    if not is_playing:
        last_id = 0
        return last_id

    # Track is the same as before so return with same id
    if track['id'] == last_id:
        return last_id

    # Update twitter
    update = updateTwitter(track)

    # If twitter update succeeded, add to spotify playlist
    if update:
        updateSpotifyPlaylist(track)
        #get_new_token()

    # Update the database
    updateDatabase(track)

    # Return the track id
    return track['id']

if __name__ == '__main__':
    if not token:
        print "Can't get token for", username
        sys.exit()
    last_id = 0
    while True:
        last_id = update(last_id)
        do_token_refresh()
time.sleep(poll_interval)
