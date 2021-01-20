import os
import logging
import random
import secrets
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram import ParseMode

import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tensorflow as tf
from tensorflow.python.framework import ops
import tflearn
import random
import json
import pickle
import string
import re

"""This is the bot secret key -- HIGHLY CONFIDENTIAL"""

TOKEN = os.environ.get("SECRET_KEY")

def load_model():
  try:
    with open("data.pickle", "rb") as f:
      words, labels, training, output = pickle.load(f)
    model.load("model.tflearn")

  except:
    print("Something seems wrong. Please ensure necessary files are present in the working directory")

def vectorize(x, words):
  vector = [0 for _ in range(len(words))]

  s_words = nltk.word_tokenize(x)
  s_words = [stemmer.stem(w.lower()) for w in s_words]
  re_puncts = re.compile('[%s]'% re.escape(string.punctuation))
  s_words = [re_puncts.sub('', w) for w in s_words]
  s_words = [w for w in s_words if w.isalpha()]

  for se in s_words:
    for i, w in enumerate(words):
      if w == se:
        vector[i] = 1

  return np.array(vector)

def start(update, context):
    welcome_text = "Hey! This is just the beginning.\nThis gumnaam bot likes to talk about IIT Mandi. Chat on!"
    context.bot.send_message(
        chat_id = update.effective_chat.id, text = welcome_text
    )


def reply(update, context):
    msg = update.message.text
    try:
      results = model.predict([vectorize(msg, words)])
      results_index = np.argmax(results)
      tag = labels[results_index]

      if results[0][results_index] > 0.8:
        for tg in data["intents"]:
          if tg["tag"] == tag:
            responses = tg["responses"]

        response = random.choice(responses)
      else :
        response = "Are you messing with me?"

    except Exception as e:
      print("Something's wrong\n", e)
      response = msg 

    context.bot.send_message(
        chat_id = update.effective_chat.id, text= response
    )

if __name__ == "__main__":
    load_model()
    
    updater = Updater(token = TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # intialise handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    reply_handler = MessageHandler( Filters.text & (~Filters.command), reply)
    dispatcher.add_handler(reply_handler)

    updater.start_polling()
    updater.idle()