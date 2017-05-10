"""
Lola the NYC Subway Bot v1.0
"""

import sys, json, traceback, requests
from flask import Flask, request
import codecs
import pymysql as mdb
import re
import sys
import datetime

# Connect to MySQL DB that holds subway information
con = mdb.connect(host = '54.173.226.134',
                  user = 'root',
                  passwd = 'dwdstudent2015',
                  charset='utf8', use_unicode=True,
                  database='mta2');

application = Flask(__name__)
app = application
PAT = 'EAAa2XBIlumsBAJsTZAPFGAMe24UEW8nhHZBPr0siwtlbdsgybjS0zXZCYrYZCJCdK3hI2EzoH1jmr1kdiRU6pwOfSzOK2INkdEh9S2VZCMXmfXPKKvSoFZCuZA1ZCtNLaQPhBlRh3cfZAOtdSGp7xMa8dpdcWEnP0RUWDnjp5L9ImkQZDZD'
VERIFICATION_TOKEN = 'verify_me'

@app.route('/', methods=['GET'])
def handle_verification():
    print ("Handling Verification.")
    if request.args.get('hub.verify_token', '') == VERIFICATION_TOKEN:
        print ("Webhook verified!")
        return request.args.get('hub.challenge', '')
    else:
        return "Wrong verification token!"



# ======================= Subway Stuff ===========================
def extract_subwayline(message):
    # Extract the line from the user message
    regex_expression = '[\s]+[1234567ACEBDFMGJZLNQRWS][\s]+'
    regex = re.compile(regex_expression,re.IGNORECASE)
    matches = regex.finditer(message)
    for match in matches:
        result = {
            "subway_line": match.group().title()
        }
        subway_line = str(result["subway_line"].strip())
        return subway_line

def subway_data_message3(subway_line):
    error_message = 'Sorry, can you try to be more clear about which train you need the status of?'
    if subway_line == None: #return error is regex search didn't find a subway line
        return error_message
    elif subway_line != None:
        subwayline = str(subway_line)
        with con:
            cur = con.cursor(mdb.cursors.DictCursor)
            # MySQL query on subway DB
            cur.execute(""" SELECT *
                         FROM subway_stats
                         INNER JOIN (SELECT line, MAX(last_update) as recent FROM subway_stats GROUP BY line) md
                             on md.line = subway_stats.line AND md.recent = subway_stats.last_update
                         WHERE md.line=%s """,subwayline)
            result = list(cur.fetchall())
            cur.close()

            status = result[0]['status']
            uptime = result[0]['uptime']

            # Dynamic response, based on current train status and train line
            t = ' Current uptime for the {sl} train is {u}%'.format(sl=subwayline, u=uptime)

            status1 = 'Good Service'
            status2 = 'Delays'
            status3 = 'Planned Work'
            status4 = 'Service Change'

            L = "Do you live in Brooklyn? Lmao that sucks. "
            W = "OoooOo the W? Do you live in the Upper East Side? Bougie AF. "
            N = "Tryna get to 8th St. - NYU? SMH bunch of bitches down there. "

            if status == status1:
                supertext = "I think you'll have good service. :)" + t
            elif status == status2:
                supertext = "Hope you're not in a rush LOL. We got delays for daysss." + t
            elif status == status3:
                supertext = "Planned work! You should probably check what's up before you leave the house today." + t
            elif status == status4:
                supertext = "Service change! Don't you just love NYC?" + t

            if subwayline == "L":
                return L + supertext
            if subwayline == "W":
                return W + supertext
            if subwayline == "N":
                return N + supertext
            else:
                return supertext







# ======================= Bot processing ===========================
@app.route('/', methods=['POST'])
def handle_messages():
    payload = request.get_data()

    # Handle messages
    for sender_id, message in messaging_events(payload):
        # Start processing valid requests
        try:
            response = processIncoming(sender_id, message)
            message = str(message)
            subway_line = extract_subwayline(message)
            answer = str(subway_data_message3(subway_line))

            if response is not None:
                send_message(PAT, sender_id, answer)

            else:
                send_message(PAT, sender_id, "Sorry I don't understand that")
        except Exception as e:
            print (e)
            traceback.print_exc()
    return "ok"

def processIncoming(user_id, message):
    if message['type'] == 'text':
        message_text = message['data']
        return message_text

    elif attachment['type'] == 'location':
        response = "I've received location (%s,%s) (y)"%(message['data'][0],message['data'][1])
        return response

    elif attachment['type'] == 'audio':
        audio_url = message['data']
        return "I've received audio %s"%(audio_url)

    # Unrecognizable incoming, remove context and reset all data to start afresh
    else:
        return "*scratch my head*"


def send_message(token, user_id, text):
    """Send the message text to recipient with id recipient.
    """
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": token},
                      data=json.dumps({
                          "recipient": {"id": user_id},
                          "message": {"text": text}
                      }),
                      headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print (r.text)

# Generate tuples of (sender_id, message_text) from the provided payload.
# This part technically clean up received data to pass only meaningful data to processIncoming() function
def messaging_events(payload):

    data = json.loads(payload.decode("utf-8"))
    messaging_events = data["entry"][0]["messaging"]

    for event in messaging_events:
        sender_id = event["sender"]["id"]

        # Not a message
        if "message" not in event:
            yield sender_id, None

        # Pure text message
        if "message" in event and "text" in event["message"] and "quick_reply" not in event["message"]:
            data = event["message"]["text"].encode('unicode_escape')
            yield sender_id, {'type':'text', 'data': data, 'message_id': event['message']['mid']}

        # Message with attachment (location, audio, photo, file, etc)
        elif "attachments" in event["message"]:

            # Location
            if "location" == event['message']['attachments'][0]["type"]:
                coordinates = event['message']['attachments'][
                    0]['payload']['coordinates']
                latitude = coordinates['lat']
                longitude = coordinates['long']

                yield sender_id, {'type':'location','data':[latitude, longitude],'message_id': event['message']['mid']}

            # Audio
            elif "audio" == event['message']['attachments'][0]["type"]:
                audio_url = event['message'][
                    'attachments'][0]['payload']['url']
                yield sender_id, {'type':'audio','data': audio_url, 'message_id': event['message']['mid']}

            else:
                yield sender_id, {'type':'text','data':"I don't understand this", 'message_id': event['message']['mid']}

        # Quick reply message type
        elif "quick_reply" in event["message"]:
            data = event["message"]["quick_reply"]["payload"]
            yield sender_id, {'type':'quick_reply','data': data, 'message_id': event['message']['mid']}

        else:
            yield sender_id, {'type':'text','data':"I don't understand this", 'message_id': event['message']['mid']}

# Allows running with simple `python <filename> <port>`
if __name__ == '__main__':
    if len(sys.argv) == 2: # Allow running on customized ports
        app.run(port=int(sys.argv[1]))
    else:
        app.run() # Default port 5000
