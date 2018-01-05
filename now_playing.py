#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import tweepy
import spotipy
import spotipy.util as util

# Keys https://apps.twitter.com/
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


# Spotify https://developer.spotify.com/my-applications/
scope = ''
client_id = ''
client_secret = ''
redirect_url = 'http://localhost/'
username = ''
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
                    track_name = results['item']['name']
                    artist_name = results['item']['artists'][0]['name']
                    cover_art = results['item']['album']['images'][0]['url']
                    track_preview = results['item']['external_urls']['spotify']
                    status_text = "#NowPlaying: " + track_name + " by " + artist_name + " " + track_preview
                    #urllib.urlretrieve(track_preview, "pics/cover_art.jpg")
                    #file = glob.glob('pics/cover_art.*')[0]
                    #api.update_with_media(file)
                    #print 'cover art: ' +str(cover_art)
                    #print 'track preview: ' +str(track_preview)
                    api.update_status(status_text)
                    print status_text
                    last_id = track_id
                    time.sleep(poll_interval)
                else:
                    time.sleep(poll_interval)
            else:
                #print "Nothing Playing..."
                last_id = 0
                time.sleep(poll_interval)
        else:
            print "Can't get token for", username
            sys.exit()

if __name__ == '__main__':
    sys.exit(main())
