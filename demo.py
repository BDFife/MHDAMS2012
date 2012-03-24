from flask import Flask
from flask import render_template
from flask import request

from secrets import apikey, sign

import urllib
import json
import time

app = Flask (__name__)

@app.route('/')
def index():
    return render_template('index.html', testName="Fella")

@app.route('/album/search/<album>')
def find_album(album):
    my_url = 'http://api.rovicorp.com/search/v2/music/search?query=' + str(album) + '&apikey=' + str(apikey()) + '&sig=' + str(sign()) + '&entitytype=album'

    f = urllib.urlopen(my_url)
    album = json.loads(f.read())

    return str(album)

@app.route('/album/info/<album>')
def show_album(album):
    my_url = 'http://api.rovicorp.com/data/v1/album/info?album=' + str(album) + '&apikey=' + str(apikey()) + '&sig=' + str(sign())

    f = urllib.urlopen(my_url)
    album = json.loads(f.read())
    top_album = album["album"]["title"]
    top_artist = album["album"]["primaryArtists"][0]["name"]

    return "Top result: " + top_album + " by " + top_artist

"""

@app.route('/show/artist/<artist>')
def show_artist(artist):

    my_url = 'http://api.rovicorp.com/data/v1/name/info?name=' + str(artist) + '&apikey=' + str(apikey()) + '&sig=' + str(sign())

    f = urllib.urlopen(my_url)
    artist = json.loads(f.read())

    print my_url
    
    artist_info = {}
    artist_info["name"] = artist["name"]["name"]
    artist_info["birth"] = artist["name"]["birth"]["date"]
    artist_info["home"] = artist["name"]["birth"]["place"]

    return render_template('artist.html', artist_info=artist_info)

@app.route('/autocomplete/<query>')
def autocomplete(query):

    autocomplete = get_autocomplete(query)

    autocomplete_info = autocomplete["autocompleteResponse"]["results"]

    return render_template('autocomplete.html', autocomplete=autocomplete_info)

@app.route('/show/name/<name>')
def show_name(name):
    return render_template('name.html', name=name)

"""

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.logger.debug('The logger is running, hooray!')
