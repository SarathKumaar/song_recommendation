import pandas as pd
from IPython.display import display
import tweepy

data_dir = "../../Desktop/SpotGenTrack/Data Sources/"
albums = pd.read_csv(data_dir + "spotify_albums.csv")
artists = pd.read_csv(data_dir + "spotify_artists.csv")
tracks = pd.read_csv(data_dir + "spotify_tracks.csv")


def join_genredate(artists_df, albums_df, tracks_df):
    album = albums_df.rename(columns={'id': "album_id"}).set_index('album_id')
    artist = artists_df.rename(columns={'id': 'artists_id', 'name': 'artists_name'}).set_index('artists_id')
    track = tracks_df.set_index('album_id').join(album['release_date'], on='album_id')
    track.artists_id = track.artists_id.apply(lambda x: x[2:-2])
    track = track.set_index('artists_id').join(artist[['artists_name', 'genres']], on='artists_id')
    track.reset_index(drop=False, inplace=True)
    track['release_year'] = pd.to_datetime(track.release_date).dt.year
    track.drop(columns=['Unnamed: 0', 'country', 'track_name_prev', 'track_number', 'type'], inplace=True)

    return track[track.release_year >= 1980]


def get_filtered_track_df(df, genres_to_include):
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    df_exploded = df.explode("genres")[df.explode("genres")["genres"].isin(genres_to_include)]
    df_exploded.loc[df_exploded["genres"] == "korean pop", "genres"] = "k-pop"
    df_exploded_indices = list(df_exploded.index.unique())
    df = df[df.index.isin(df_exploded_indices)]
    df = df.reset_index(drop=True)

    return df


genres_to_include = genres = ['dance pop', 'electronic', 'electropop',
                              'hip hop', 'jazz', 'k-pop', 'latin', 'pop', 'pop rap', 'r&b', 'rock']
track_with_year_and_genre = join_genredate(artists, albums, tracks)
filtered_track_df = get_filtered_track_df(track_with_year_and_genre, genres_to_include)

filtered_track_df["uri"] = filtered_track_df["uri"].str.replace("spotify:track:", "")
filtered_track_df = filtered_track_df.drop(columns=['analysis_url', 'available_markets'])

display(filtered_track_df.head(10))

filtered_track_df.to_csv("filtered_track_df1980.csv", index=False)

