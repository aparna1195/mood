import os
import spotipy
from flask import Flask, request, redirect, session, render_template
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import lyricsgenius 

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.secret_key = "your_super_secret_key"
app.config['SESSION_COOKIE_NAME'] = 'Spotify-Session'

# Spotify Auth
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-library-read user-read-recently-played user-top-read user-read-private user-read-email"
)

genius = lyricsgenius.Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
analyzer = SentimentIntensityAnalyzer()

def get_lyrics(artist, title):
    try:
        song = genius.search_song(title, artist)
        return song.lyrics if song else "Lyrics not found"
    except Exception as e:
        print(f"Error fetching lyrics for {title} by {artist}: {e}")
        return "Lyrics not available"

@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect('/mood')

@app.route('/mood', methods=['GET', 'POST'])
def mood():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])

    if request.method == 'POST':
        selected_mood = request.form.get('mood')
        top_tracks = sp.current_user_top_tracks(limit=50)['items']
        valid_tracks = [t for t in top_tracks if t and t.get('id')]

        results = []

        for track in valid_tracks:
            title = track['name']
            artist = track['artists'][0]['name']
            lyrics = get_lyrics(artist, title)
            sentiment = analyzer.polarity_scores(lyrics)
            compound = sentiment['compound']

            match = (
    (selected_mood == 'Mellow' and compound > 0.2) or
    (selected_mood == 'happy' and compound > 0.4) or
    (selected_mood == 'sad' and compound < -0.0) or
    (selected_mood == 'chill' and -0.0 <= compound <= 0.2)
)


            if match:
                results.append({
                    'title': title,
                    'artist': artist,
                    'lyrics': lyrics,
                    'sentiment': sentiment
                })
            

        return render_template('mood.html', mood=selected_mood, lyrics_by_track=results)

    return render_template('mood.html', mood=None, lyrics_by_track=None)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
