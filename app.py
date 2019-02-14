#!/usr/bin/env python3
import json
import math
import os
from pprint import pprint

import requests
from chalice import Chalice

SLACK_URL = 'https://slack.com/api/chat.'
IGNORE_SLUG = 'ignore_entropy'
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ENTROPY_THRESHOLD = 4.5

app = Chalice(app_name='entropy-checker')

class SlackBot:
    def __init__(self, channel, text, user, event_ts, **_):
        self.channel = channel
        self.text = text
        self.user = user
        self.timestamp = event_ts
        self.entropy = 0

    def check_entropy(self):
        print('checking entropy')
        if IGNORE_SLUG in self.text:
            return
        elif self._calculate_entropy() > ENTROPY_THRESHOLD:
            self.delete_message()
            self.post_message()

    def delete_message(self):
        delete_url = SLACK_URL + 'delete'
        data = {
            'token': BOT_TOKEN,
            'channel': self.channel,
            'ts': self.timestamp
        }
        requests.post(delete_url, data)

    def post_message(self):
        print('posting message')
        post_url = SLACK_URL + 'postMessage'
        attachments = self._generate_message_attachments()
        message = 'Your message has been deleted for containing a high entropy string.\n'
        message += 'To avoid your message from being deleted, add `{0}` somewhere in the message'
        message = message.format(IGNORE_SLUG)
        data = {
            'token': BOT_TOKEN,
            'channel': self.channel,
            'text': message,
            'attachments': attachments
        }
        response = requests.post(post_url, data)
        print('RESPONSE {0}'.format(response))

    def _generate_message_attachments(self):
        attachments = [{'text': 'String entropy: {0}'.format(self.entropy)}]
        return json.dumps(attachments)

    def _calculate_entropy(self):
        self.entropy = 0
        for i in range(256):
            character = chr(i)
            probability = float(self.text.count(character)) / len(self.text)
            if probability > 0:
                self.entropy -= probability * math.log(probability, 2)

        print('ENTROPY: {0}'.format(self.entropy))
        return self.entropy


@app.route('/', methods=['POST'])
def index():
    request_body = app.current_request.json_body
    if 'event' in request_body:
        event = request_body['event']
        if event['type'] == 'message' and event.get('subtype') is None:
            bot = SlackBot(**event)
            bot.check_entropy()
    if request_body:
        return request_body.get('challenge', 'OK')
    else:
        return 'null'

@app.route('/action', methods=['POST'])
def action():
    request_body = app.current_request.json_body
    pprint(request_body)
