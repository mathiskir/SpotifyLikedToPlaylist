import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-modify-public playlist-modify-private user-library-read user-library-modify"
))

PLAYLIST_ID = os.getenv("PLAYLIST_ID")

liked_tracks = []
track_ids = set()
results = sp.current_user_saved_tracks()

if not results['items']:
    print("Keine Liked Songs gefunden. Das Skript wird abgebrochen.")
    exit()

while results:
    for item in results['items']:
        track = item['track']
        track_id = track['id']
        if track_id not in track_ids:
            track_ids.add(track_id)
            liked_tracks.append(track_id)
    results = sp.next(results) if results['next'] else None

print(f"{len(liked_tracks)} Liked Songs abgerufen.")

playlist_tracks = set()
playlist_results = sp.playlist_tracks(PLAYLIST_ID)
while playlist_results:
    for item in playlist_results['items']:
        if item['track']:
            playlist_tracks.add(item['track']['id'])
    playlist_results = sp.next(playlist_results) if playlist_results['next'] else None

print(f"{len(playlist_tracks)} Songs in der Playlist gefunden.")

if not liked_tracks:
    print("Keine Liked Songs zum Hinzufügen gefunden.")
    exit()
if not playlist_tracks:
    print("Keine Songs in der Ziel-Playlist gefunden.")
    exit()

new_tracks = [track for track in liked_tracks if track not in playlist_tracks]

duplicate_tracks = [track for track in liked_tracks if track in playlist_tracks]
print(f"{len(new_tracks)} neue Songs und {len(duplicate_tracks)} Duplikate erkannt.")

if new_tracks:
    sp.playlist_add_items(PLAYLIST_ID, new_tracks)
    print(f"{len(new_tracks)} neue Songs zur Playlist hinzugefügt!")
else:
    print("Keine neuen Songs gefunden.")

tracks_to_remove = new_tracks + duplicate_tracks
if tracks_to_remove:
    for i in range(0, len(tracks_to_remove), 50):
        batch = tracks_to_remove[i:i + 50]
        print(f"Entferne folgende Tracks aus den Liked Songs: {batch}")
        sp.current_user_saved_tracks_delete(batch)
    print(f"{len(tracks_to_remove)} Songs aus den gelikten entfernt.")
else:
    print("Keine Songs zum Entfernen.")

remaining_tracks = set()
results = sp.current_user_saved_tracks()
while results:
    for item in results['items']:
        remaining_tracks.add(item['track']['id'])
    results = sp.next(results) if results['next'] else None

if any(track in remaining_tracks for track in tracks_to_remove):
    print("Warnung: Einige Songs wurden nicht erfolgreich entfernt!")
else:
    print("Alle hinzugefügten und doppelten Songs wurden erfolgreich aus den gelikten entfernt.")