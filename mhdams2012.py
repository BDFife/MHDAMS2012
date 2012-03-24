from flask import Flask
from flask import request

from secrets import apikey, sign

import urllib
import json
import time

import twilio.twiml

app = Flask (__name__)


def msg_trim(msg, msg_array):
	if len(msg) < 160:
		msg_array.append(msg)
	else:
		index = msg.rfind('#', 0, 160)
		index = (index + 1)
		msg_array.append(msg[:index])
		msg_trim(msg[index:], msg_array)	
	return msg_array

"""
def msg_trim(msg):
    msg_array = [ ] 
    if len(msg_trim) < 160:
        msg_array.append(msg)
        return msg
    else:
        index = msg.rfind('\r\n', 0, 160)
        msg_array.append(msg[:(index+1)])
        msg_trim(msg[(index+1):])
"""

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        resp = twilio.twiml.Response()
        resp.sms(str("You said: " + request.form["Body"]))
        return str(resp)

    if request.method == 'GET':
        resp = twilio.twiml.Response()
        resp.sms("This starbase is fully operational")
        return str(resp)


@app.route('/album/search/<album>')
def find_album(album):
    my_url = 'http://api.rovicorp.com/search/v2/music/search?query=' + str(album) + '&apikey=' + str(apikey()) + '&sig=' + str(sign()) + '&entitytype=album'

    f = urllib.urlopen(my_url)
    album = json.loads(f.read())

    return str(album)

@app.route('/album/info/', methods=['POST', 'GET'])
def show_album():
    if request.method == 'GET':
        resp = twilio.twiml.Response()
        resp.sms("You need to use a POST method with this URL")
        return str(resp)

    if request.method == 'POST':
        album_name = request.form.get("Body")
        my_url = 'http://api.rovicorp.com/data/v1/album/info?album=' + str(album_name) + '&apikey=' + str(apikey()) + '&sig=' + str(sign())

        f = urllib.urlopen(my_url)
        album = json.loads(f.read())
        top_album = album["album"]["title"]
        top_artist = album["album"]["primaryArtists"][0]["name"]

        resp= twilio.twiml.Response()
        resp.sms("Top result: " + top_album + " by " + top_artist)
        # resp.sms("Will this send two messages?")
        # yes, it will.
        return str(resp)

@app.route('/artist/discography/', methods=['POST', 'GET'])
def show_discography():
    if request.method == 'GET':
        resp = twilio.twiml.Response()
        resp.sms("You need to use a POST method with this URL")
        return str(resp)
    
    if request.method == 'POST':
        artist_name = request.form.get("Body")

        my_url = 'http://api.rovicorp.com/data/v1/name/discography?name=' + str(artist_name) + '&type=main' + '&count=14'+ '&format=json' + '&apikey=' + str(apikey()) + '&sig=' + str(sign()) 

        f = urllib.urlopen(my_url)
        discography = json.loads(f.read())

        album_str = ""
        for albums in discography['discography']:
            album_str = album_str + albums.get('title') + " " + albums.get('year')[:4] + "\r\n"

        # now chop the string into 160 character chunks. 
        msg_array = [ ]
        msg_trim(album_str, msg_array)
        #resp= twilio.twiml.Response()
        #for message in msg_array:
        #    resp.sms(message)
        #return str(resp)
        resp= twilio.twiml.Response()
        resp.sms("hello")
        return str(resp)



"""
    my_url = 'http://api.rovicorp.com/data/v1/album/info?album=' + str(album) + '&apikey=' + str(apikey()) + '&sig=' + str(sign())

    f = urllib.urlopen(my_url)
    album = json.loads(f.read())
    top_album = album["album"]["title"]
    top_artist = album["album"]["primaryArtists"][0]["name"]

    resp = twilio.twiml.Response()
    resp.sms( "Top result: " + top_album + " by " + top_artist)
    return str(resp)

    #return "Top result: " + top_album + " by " + top_artist
"""
if __name__ == '__main__':
    app.debug = False
    app.run()
    app.logger.debug('The logger is running, hooray!')
