import requests
import sqlalchemy
import pandas as pd
import json
from datetime import datetime
import datetime
import sqlite3

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "ronogenu-4605"
TOKEN = "BQCoORrl1jSkBaWEMslWzk8J9XwkzCNnbhn7Os2BVAo9yrg9mzc8nZ5lQmNZCCxkJsN2APpRBgHRqNGT4VOCcnuPLNk_N0ZCmMRandNFpExDOXH-IjjBQAzXoXel642qx5Ob4hAnpfI7Or398y-4"

# Extract Stage

if __name__ == "__main__":

    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=TOKEN)
    }

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

r = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50&&after={time}".format(time=yesterday_unix_timestamp),headers = headers)
data = r.json()

song_names = []
artist_names = []
played_at_list = []
timestamps = []

for song in data["items"]:
    song_names.append(song['track']['name'])
    artist_names.append(song['track']['album']['artists'][0]['name'])
    played_at_list.append(song['played_at'])
    timestamps.append(song['played_at'][0:10])

song_dict = {
    "song_name" : song_names,
    "artist_name" : artist_names,
    "played_at" : played_at_list,
    "timestamp" : timestamps
}

song_df = pd.DataFrame(song_dict, columns = ['song_name','artist_name','played_at','timestamp'])
print(song_df)

# Transform: Validation Stage

def check_if_valid_data(df: pd.DataFrame):
    # Check if DataFrame is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False

    # Primary Key check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key Check is violated")

    #Check for Nulls
    if df.isnull().values.any():
        raise Exception("Null value found")

    #Check that all timestamp are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    yesterday = yesterday.replace(hour = 0, minute=0,second=0,microsecond=0)

    timestamps = df['timestamp'].to_list()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
            raise Exception("At least one of the returned songs does not come from within the last 24 hours")
    return True

if check_if_valid_data(song_df):
    print("Data Valid, proceed to load stage")

# Load Stage

engine = sqlalchemy.create_engine(DATABASE_LOCATION)
conn = sqlite3.connect('my_played_tracks.db')
cursor = conn.cursor()

sql_query = """
CREATE TABLE IF NOT EXISTS my_played_tracks(
    song_name VARCHAR(200),
    artist_name VARCHAR(200),
    played_at DATE PRIMARY KEY,
    timestamp TIMESTAMP
)
"""

cursor.execute(sql_query)
print("Opened Database Successfully")

try:
    song_df.to_sql("my_played_tracks",engine,index=False,if_exists='append')
except:
    print("Data already exists in the database")

conn.close()
print("Closed Database Successfully")