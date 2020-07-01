import telebot
import config
import schedule
import datetime
import os
from flask import Flask, request

TOKEN = config.TOKEN
WEB_URL = config.WEB_URL

open_time = datetime.time(hour=16, minute=55, second=0)
close_time = open_time.replace(hour=open_time.hour + 5)
open_time_str = open_time.strftime("%H:%M:%S")

bot = telebot.TeleBot(TOKEN)
job = schedule.every().day.at(open_time_str)
# job = schedule.every(5).seconds
is_run = False

server = Flask(__name__)


@bot.message_handler(commands=['help'])
def help_handle(message):
    bot.send_message(message.chat.id, "it is a simple bot, that can schedule poll. "
                                      "Now it can only send poll every day at 15:00 but in future "
                                      "I am going to add ability to schedule your time and poll")


@bot.message_handler(commands=['start'])
def start_handle(message):
    global is_run
    if not is_run:
        is_run = True

        job.do(bot.send_poll, chat_id=message.chat.id,
               question="Lets roll today!",
               options=["20:00", "21:00", "another time", "not today"],
               is_anonymous=False,
               allows_multiple_answers=True,
               close_date=close_time)

        while is_run:
            schedule.run_pending()


@bot.message_handler(commands=['stop'])
def stop_handle(message):
    global is_run
    if is_run:
        schedule.cancel_job(job)
        is_run = False


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
