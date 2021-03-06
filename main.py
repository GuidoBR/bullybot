# -*- coding: utf-8 -*-
import json
import logging
import urllib
import urllib2

from bot import resposta
import bot

# for sending images
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2
import re

TOKEN = '168191309:AAEdER88qh8Q34Hdt-yUZSBNhiU_mMfMUOw'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================


class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


def findWholeWord(word, text):
    return re.compile(
        r'\b({0})\b'.format(word),
        flags=re.IGNORECASE
    ).search(text)

# ================================


class MeHandler(webapp2.RequestHandler):

    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(
            json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe')))
        )


class GetUpdatesHandler(webapp2.RequestHandler):

    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(
            json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates')))
        )


class SetWebhookHandler(webapp2.RequestHandler):

    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(
                json.load(
                    urllib2.urlopen(
                        BASE_URL + 'setWebhook', urllib.urlencode({'url': url}))
                )
            )
            )


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        message = body['message']
        message_id = message.get('message_id')
        text = message.get('text')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(
                    BASE_URL + 'sendMessage',
                    urllib.urlencode(
                        {
                            'chat_id': str(chat_id),
                            'text': msg.encode('utf-8'),
                            'disable_web_page_preview': 'true',
                            'reply_to_message_id': str(message_id),
                        }
                    )
                ).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        # CUSTOMIZE FROM HERE
        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/bomdia':
                reply(msg=bot.bomdia())
            elif text == '/gutenmorgen':
                reply(msg=bot.gutenMorgen())
            elif text == '/image':
                reply(img=bot.drawImage())
            elif text == '/ingrid':
                reply(msg=resposta('ingrid').get('msg'))
            elif text == '/codigo':
                reply(msg=resposta('codigo').get('msg'))
        else:
            text_search = {
                'romero britto': {'img': bot.romero()},
                'Romero Britto': {'img': bot.romero()},
                'nude': {'img': bot.nude()},
                'sex': resposta('sex'),
                'sexo': resposta('sex'),
                'elingrid': resposta('elingrid'),
                'carlisa': resposta('carlisa'),
                'lumateus': resposta('lumateus'),
                'lotr': resposta('lotr'),
                'Gandalf': resposta('lotr'),
                'Gimli': resposta('lotr'),
                'alemanha': resposta('alemanha'),
                'starwars': resposta('starwars'),
                'SW': resposta('starwars'),
                'Star Wars': resposta('starwars'),
                'boa noite': resposta('boanoite'),
                'who are you': 'https://www.youtube.com/watch?v=Qh8SsaCWY-s',
                'mochileiro': resposta('guia'),
                'what time': resposta('hora'),
                'GoT': resposta('got'),
                'game of thrones': resposta('got'),
                'dbz': resposta('dbz'),
                'Dragon Ball': resposta('dbz'),
                'corretor': resposta('corretor'),
            }

            for key, value in text_search.iteritems():
                if findWholeWord(key, text):
                    reply(msg=value.get('msg'), img=value.get('img'))

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
