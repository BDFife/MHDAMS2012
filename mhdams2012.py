from flask import Flask
from flask import request
from flask import url_for, redirect
from flask import render_template

from secrets import apikey, sign

import urllib
import json
import time

import twilio.twiml
import re

app = Flask (__name__)

def msg_trim(msg, msg_array, br_char):
    if len(msg) < 160:
        msg_array.append(msg)
    else:
        index = msg.rfind(br_char, 0, 160)
        index += 1
        msg_array.append(msg[:index])
        msg_trim(msg[index:], msg_array, br_char)
    return msg_array

def scrub_links(text):
    remove_links = re.compile(r"""\[.*?\]""")
    new_text = remove_links.sub("", text)
    return new_text

def cmd_parse(cmd):
    command_ref = re.compile(r"""
        [\s]*               # allow initial whitespace
        (?P<cmd>            # identify as the "command"
         name|              # artist name
         album|             # album name
         bio|               # artist biography
         review|            # album review
         song)              # song info
        [\s]+               # allow interim whitespace
        (?P<data>           # identify as the "data"
         .+)                # (data is any remaining chars)
                            # TBD, make non-greedy, 
                            # trim whitespace
    """, re.VERBOSE)

    # add in a lowercase coercion to make things simpler. 
    cmd = cmd.lower()
    result = command_ref.match(cmd)
    # if no match was found, result will be None
    if result:
        my_cmd = result.group('cmd')
        my_data = result.group('data')
    else:
        my_cmd = "info"

        my_data = 'garbage'
    return my_cmd, my_data

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        cmd_text = request.form.get("Body")
        cmd, data = cmd_parse(cmd_text)
        return redirect(url_for(cmd, data=data))

@app.route('/commands/info/<data>', methods=['POST', 'GET'])
def info(data):
    resp = twilio.twiml.Response()
    resp.sms("Valid commands are name, song, bio, album, review. \r\nExample: 'name bieber'")
    return str(resp)

@app.route('/song/info/<data>', methods=['POST', 'GET'])
def song(data):
    my_url = 'http://api.rovicorp.com/data/v1/song/info?track=' + str(data) + "&apikey=" + str(apikey()) + "&sig=" + str(sign())

    f = urllib.urlopen(my_url)

    song = json.loads(f.read())
    top_song = song["song"]["title"]
    top_artist = song["song"]["primaryArtists"][0]["name"]

    resp = twilio.twiml.Response()
    resp.sms("Top result: " + top_song + " by " + top_artist + ".")
    return str(resp)

@app.route('/album/info/<data>', methods=['POST', 'GET'])
def album(data):
    my_url = 'http://api.rovicorp.com/data/v1/album/info?album=' + str(data) + '&apikey=' + str(apikey()) + '&sig=' + str(sign())

    f = urllib.urlopen(my_url)
    album = json.loads(f.read())
    top_album = album["album"]["title"]
    top_artist = album["album"]["primaryArtists"][0]["name"]
    release_date = album["album"]["originalReleaseDate"]

    resp= twilio.twiml.Response()
    resp.sms("Top result: " + top_album + " by " + top_artist + ". Released on " + str(release_date) + ".")
    return str(resp)

@app.route('/artist/discography/<data>', methods=['POST', 'GET'])
def name(data):
    my_url = 'http://api.rovicorp.com/data/v1/name/discography?name=' + str(data) + '&type=main' + '&format=json' + '&apikey=' + str(apikey()) + '&sig=' + str(sign()) 
    
    f = urllib.urlopen(my_url)
    discography = json.loads(f.read())
    
    album_str = ""
    for albums in discography['discography']:
        album_str = album_str + albums.get('title') + " " + albums.get('year')[:4] + "\r\n"
    
    # now chop the string into 160 character chunks. 
    msg_array = [ ]
    msg_trim(album_str, msg_array, '\r\n')

    resp= twilio.twiml.Response()
    for message in msg_array:
        resp.sms(message)
    return str(resp)

@app.route('/artist/bio/<data>', methods=['POST', 'GET'])
def bio(data):
    my_url = 'http://api.rovicorp.com/data/v1/name/musicbio?name=' + str(data) + '&format=json' + '&apikey=' + str(apikey()) + '&sig=' + str(sign())
    
    f = urllib.urlopen(my_url)
    biography = json.loads(f.read())

    bio_text = "Sorry, no bio available"
    music_bio = biography.get("musicBio")

    if music_bio:
        music_overview = music_bio.get("musicBioOverview")
        if music_overview:
            bio_text = music_overview[0].get("overview")
    bio_text = scrub_links(bio_text)

    # chop to 160 chunks
    msg_array = [ ] 
    msg_trim(bio_text, msg_array, " ")

    resp = twilio.twiml.Response()
    for message in msg_array:
        resp.sms(message)
    return str(resp)

@app.route('/album/review/<data>', methods=['POST', 'GET'])
def review(data):
    my_url = 'http://api.rovicorp.com/data/v1/album/primaryreview?album=' + str(data) + '&format=json' + '&apikey=' + str(apikey()) + '&sig=' + str(sign())

    f = urllib.urlopen(my_url)
    review = json.loads(f.read())
    
    review_text = "Sorry, no album review available"
    album_review = review.get('primaryReview')
    if album_review:
        review_text = album_review.get('text')
    review_text = scrub_links(review_text)

    # chop
    msg_array = [ ]
    msg_trim(review_text, msg_array, " ")
    
    resp = twilio.twiml.Response()
    for message in msg_array:
        resp.sms(message)
    return str(resp)

if __name__ == '__main__':
    app.debug = False
    app.run()
    app.logger.debug('The logger is running, hooray!')
