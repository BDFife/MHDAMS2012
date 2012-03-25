from flask import Flask
from flask import request
from flask import url_for, redirect

from secrets import apikey, sign

import urllib
import json
import time

import twilio.twiml
import re

app = Flask (__name__)

def msg_trim(msg, msg_array):
    if len(msg) < 160:
        msg_array.append(msg)
    else:
        index = msg.rfind('\r\n', 0, 160)
        index += 1
        msg_array.appebnd(msg[:index])
        msg_trim(msg[index:], msg_array)
    return msg_array

def cmd_parse(cmd):
    command_ref = re.compile(r"""
        [\s]*               # allow initial whitespace
        (?P<cmd>            # identify as the "command"
         name|              # artist name
         album|             # album name
         bio|               # artist biography
         review)            # album review
        [\s]+               # allow interim whitespace
        (?P<data>           # identify as the "data"
         .+)                # (data is any remaining chars)
                            # TBD, make non-greedy, 
                            # trim whitespace
    """, re.VERBOSE)

    result = command_ref.match(cmd)
    # if no match was found, result will be None
    if result:
        my_cmd = result.group('cmd')
        my_data = result.group('data')
    else:
        my_cmd = 'help'
        my_data = None
    return my_cmd, my_data

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        resp = twilio.twiml.Response()
        resp.sms("This needs to be a POST")
        return str(resp)

    if request.method == 'POST':
        cmd_text = request.form.get("Body")
        cmd, data = cmd_parse(cmd_text)
        #resp = twilio.twiml.Response()
        #resp.sms("You asked for " + str(cmd )+ " of " + str(data))
        #return str(resp)
        return redirect(url_for(cmd, data=data))
                        
@app.route('/album/info/<data>', methods=['POST', 'GET'])
def album(data):
    my_url = 'http://api.rovicorp.com/data/v1/album/info?album=' + str(data) + '&apikey=' + str(apikey()) + '&sig=' + str(sign())

    f = urllib.urlopen(my_url)
    album = json.loads(f.read())
    top_album = album["album"]["title"]
    top_artist = album["album"]["primaryArtists"][0]["name"]

    resp= twilio.twiml.Response()
    resp.sms("Top result: " + top_album + " by " + top_artist)
    return str(resp)

@app.route('/artist/discography/', methods=['POST', 'GET'])
def show_discography():
    if request.method == 'GET':
        resp = twilio.twiml.Response()
        resp.sms("You need to use a POST method with this URL")
        return str(resp)
    
    if request.method == 'POST':
        artist_name = request.form.get("Body")
        my_url = 'http://api.rovicorp.com/data/v1/name/discography?name=' + str(artist_name) + '&type=main' + '&format=json' + '&apikey=' + str(apikey()) + '&sig=' + str(sign()) 
        f = urllib.urlopen(my_url)
        discography = json.loads(f.read())
        album_str = ""
        for albums in discography['discography']:
            album_str = album_str + albums.get('title') + " " + albums.get('year')[:4] + "\r\n"

        # now chop the string into 160 character chunks. 
        msg_array = [ ]
        msg_trim(album_str, msg_array)
        resp= twilio.twiml.Response()
        for message in msg_array:
            resp.sms(message)
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
