#!/usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, session, request, redirect
import json
import time
import pandas as pd

# App config
app = Flask(__name__)

app.secret_key = "1f4cf08aab1f5da059e25a3f27b80ba"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Replace with your Spotify API credentials
SPOTIPY_CLIENT_ID = 'd48ab9fbd0904ea99f4503bec281f85f'
SPOTIPY_CLIENT_SECRET = 'efd74e1c1b7b46b6b4d682134c54171b'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/authorize'  # Update with your redirect URI

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="user-library-read"
    )

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/getTracks")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/getTracks')
def get_all_tracks():
    token_info, authorized = get_token()
    if not authorized:
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info.get('access_token'))
    results = []

    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        cur_group = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(cur_group):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results.append(val)
        if len(cur_group) < 50:
            break

    df = pd.DataFrame(results, columns=["song names"])
    df.to_csv('songs.csv', index=False)
    return "done"

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    if not session.get('token_info', False):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if is_token_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

if __name__ == '__main__':
    app.run(debug=True)
