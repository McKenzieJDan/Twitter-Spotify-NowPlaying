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

poll_interval = 20

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
                    # Twitter Status
                    track_name = results['item']['name']
                    artist_name = results['item']['artists'][0]['name']
                    track_preview = results['item']['external_urls']['spotify']
                    tweet_text = "#NowPlaying: " + track_name + " by " + artist_name + " " + track_preview
                    # Twitter Profile Images
                    cover_art = results['item']['album']['images'][0]['url']
                    urllib.urlretrieve(cover_art, "profile_image.jpg")
                    profile_image = 'profile_image.jpg'
                    # Spotify Playlist
                    playlist_id = spotify_playlist
                    track_uri = results['item']['uri']
                    track_uri_latest = [track_uri]
                    try:
                        api.update_status(tweet_text)
                        api.update_profile_image(profile_image)
                        api.update_profile_banner(profile_image)
                        update = True
                    except tweepy.error.TweepError:
                        update = False
                        pass
                    if update == True:
                        sp.user_playlist_add_tracks(username, playlist_id, track_uri_latest, position=0)
                        try:
                            sqlite_file = 'now_playing.db'
                            conn = sqlite3.connect(sqlite_file)
                            c = conn.cursor()
                            album_name = results['item']['album']['name']
                            name = str(track_name)
                            c.execute('SELECT 1 FROM nowplaying WHERE track=? LIMIT 1', (name,))
                            name_exists = c.fetchone() is not None
                            if name_exists is False:
                                c.execute("INSERT OR IGNORE INTO nowplaying (track, artist, album, totalPlays, firstListen) VALUES ('{a1}', '{a2}', '{a3}', 1, datetime('now'))".\
                                          format(a1=track_name, a2=artist_name, a3=album_name))
                                #print "Added to database"
                            else:
                                c.execute("UPDATE nowplaying SET totalPlays = totalPlays + 1 WHERE track = '{a1}'".\
                                          format(a1=track_name))
                                c.execute("UPDATE nowplaying SET lastListen = datetime('now') WHERE track = '{a1}'".\
                                          format(a1=track_name))
                                #print "Updated play count"
                            conn.commit()
                            conn.close()
                        except sqlite3.Error as er:
                            print 'er:', er.message
                            pass
                    else:
                        try:
                            sqlite_file = 'now_playing.db'
                            conn = sqlite3.connect(sqlite_file)
                            c = conn.cursor()
                            album_name = results['item']['album']['name']
                            name = str(track_name)
                            c.execute('SELECT 1 FROM nowplaying WHERE track=? LIMIT 1', (name,))
                            name_exists = c.fetchone() is not None
                            if name_exists is False:
                                c.execute("INSERT OR IGNORE INTO nowplaying (track, artist, album, totalPlays, firstListen) VALUES ('{a1}', '{a2}', '{a3}', 1, datetime('now'))".\
                                          format(a1=track_name, a2=artist_name, a3=album_name))
                                #print "Added to database"
                            else:
                                c.execute("UPDATE nowplaying SET totalPlays = totalPlays + 1 WHERE track = '{a1}'".\
                                          format(a1=track_name))
                                c.execute("UPDATE nowplaying SET lastListen = datetime('now') WHERE track = '{a1}'".\
                                          format(a1=track_name))
                                #print "Updated play count"
                            conn.commit()
                            conn.close()
                        except sqlite3.Error as er:
                            print 'er:', er.message
                            pass
                        pass
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
