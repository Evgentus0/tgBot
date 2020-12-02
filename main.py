import telebot
import config
import schedule
import datetime
import os
from flask import Flask, request

from googleapiclient.discovery import build

APIKEY = config.API_KEY
TOKEN = config.TOKEN
WEB_URL = config.WEB_URL

lang_service = build('language', 'v1beta1', developerKey=APIKEY)

bot = telebot.TeleBot(TOKEN)
is_run = False
server = Flask(__name__)


def analyze_text(text):
    response = lang_service.documents().analyzeSyntax(
        body={
            'document': {
                'type': 'PLAIN_TEXT',
                'content': text
            }
        }
    ).execute()

    tokens = response['tokens']
    del tokens[0:2]

    result = "Number of words: " + str(len(tokens)) + "\n"
    for token in tokens:
        result += str(token['text']['content']) + " - is " + str(token['partOfSpeech']['tag'])
        if token['partOfSpeech']['tag'] == 'VERB':
            result += ". Time of verb is " + str(token['partOfSpeech']['tense'])

        result += "\n"

    return result


@bot.message_handler(commands=['help'])
def help_handle(message):
    bot.send_message(message.chat.id, "Bot help you to understand feeling of entering fraze")


@bot.message_handler(commands=['start'])
def start_handle(message):
    text = message.text
    result = analyze_text(text)
    bot.send_message(message.chat.id, result)


# bot.polling(none_stop=True)
@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url=WEB_URL + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
