# Table of Contents

- Introduction
- Setting up the Environment
- ETL Process
  - Extracting Data from Spotify
  - Transforming the Data
  - Loading the Data to a Database
- Scheduling using Airflow
  - Setting up Airflow Environment
  - Running Airflow
- Challenges Encountered during Project Creation
- Useful Resources

## Introduction

I made this project to learn and practice the basic skills needed in the field of Data Engineering. This documentation originated from a need to determine if I truly comprehended what I was doing.

This project will walk you through the Extract-Transform-Load (ETL) process and how to automate it. This isn't meant to be a full-fledged project, but it will get you started on understanding the framework for creating an end-to-end Data Engineering pipeline.

This project also assumes that the person completing it has a basic understanding of Python and SQL. Nonetheless, considering this is my first venture into the subject of Data Engineering, I'll do my best to make the documentation as user-friendly as possible.

Throughout this project, I'm using powershell most of the time since I am more comfortable with it for now but I'm also using bash especially in setting airflow.

## Setting up the Environment

This section walks you through the steps of setting up a virtual environment and installing the project's required libraries. The purpose of creating a virtual environment is to manage the project's settings and dependencies while also making it reproducible.

To start with, we need to install  virtualenv:

<pre><code> pip install virtualenv </pre></code>

After that, we make our virtual environment, which we call spotify-env:

<pre><code> virtualenv spotify-env </pre></code>

> Check if a spotify-env folder has been created in your working directory to see if your environment has been generated.

Let's get our Python environment up and running:

<pre><code> spotify-env/Scripts/activate </pre></code>

Lastly, let us install the required modules for this project:

<pre><code>pip install requests
pip install sqlalchemy
pip install pandas
pip install sqlite3
</pre></code>

Why do we need these modules?

- We will be using [**requests**](https://docs.python-requests.org/en/master/) to access our Spotify account using Spotify API.
- We will be using [**sqlalchemy**](https://www.sqlalchemy.org) to facilitate the communication of our program to our databases.
- We will be using [**pandas**](https://pandas.pydata.org/) to wrangle our data and create our dataframe.
- We will be using [**sqlite3**](https://www.sqlite.org/index.html) to create our database.

## ETL Process

### Extracting Data from Spotify

You must have a Spotify account and connect it to [Spotify Developer](https://developer.spotify.com/dashboard/) in order to access data from Spotify. Navigate to this [Endpoint](https://developer.spotify.com/console/get-recently-played/) once you've connected and you'll see the image below.

![Spotify](images/spotify_image.png)

The OAuth Token, which we will use to access information from the account, is the most critical piece of information we need from this page. Simply click the get token - green button at the bottom and choose the scope for user-read-recently-played only to request a token.
> Note that the token expires every 5 minutes so you may need to request token frequently.

![Spotify_Scope](images/spotify_scope.png)

Let's start structuring how and what information we'll retrieve now that we've already set up our Spotify account. First, we must specify our variables, which are:

<pre><code>USER_ID = "Input your User ID here"
TOKEN = "Input the generated Token here"
</pre></code>

We'll also follow the Spotify API's pre-defined instructions:

<pre><code>headers = {
    "Accept" : "application/json",
    "Content-Type" : "application/json",
    "Authorization" : "Bearer {token}".format(token=TOKEN)
    }
</pre></code>

We will program the extraction to be daily so we must define a time variable in Unix format to look for songs played the day before.

<pre><code>today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000
</pre></code>

We'll now start extracting data and save it in json format.

<pre><code>r = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50&&after={time}".format(time=yesterday_unix_timestamp),headers = headers)
data = r.json()
</pre></code>
> You can try to validate if this is successful by  printing the data.

Get only the information you need and convert it to a dataframe. In this case, I only want to see the title of the music, the artist's name, the day it was played, and the timestamp.

<pre><code>song_names = []
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
</pre></code>

>Finding the correct subset of data in the json file is the most difficult thing here. I recommend that the reader do further research and practice on this subject.

That's it. We've completed the extraction process!
