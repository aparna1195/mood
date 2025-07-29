# Spotify Mood Analysis App 🎧

A Flask app that connects to Spotify, fetches your top 50 tracks, and uses VADER sentiment analysis to classify them by mood.

## Features
- OAuth2-based Spotify login
- Fetches user's top tracks
- Analyzes mood using sentiment from track titles
- Filters tracks by mood

## Tech Stack
- Flask
- Spotipy (Spotify API)
- VADER Sentiment (NLTK)
- Python

## Setup Instructions
```bash
pip install -r requirements.txt
python app.py
