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

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.logger.debug('The logger is running, hooray!')
