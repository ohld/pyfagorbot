#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.

This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import re
import os
import random
import logging
from time import sleep

import telegram
from telegram.error import NetworkError, Unauthorized
from py_translator import Translator
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
update_id = None

TRANSLATE_ATTEMPTS = 5
CYRILLIC_SYMBOLS = "йцукенгшщзхъёэждлорпавыфячсмитьбю"
WORDS_TO_GENERATE_RANGE = range(5, 12)
WORDS_FROM_MESSAGE_RANGE = range(1, 5)
GENERATED_WORD_LENGTH_RANGE = range(3, 6)

GENERATED_TEXT_LENGTH = max(GENERATED_WORD_LENGTH_RANGE) * max(WORDS_TO_GENERATE_RANGE)

def longest_substring_finder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer

def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(TOKEN)

    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1

def generate_text(length=GENERATED_TEXT_LENGTH):
    return ''.join(random.choices(CYRILLIC_SYMBOLS, k=length))

def generate_words(k_range=WORDS_TO_GENERATE_RANGE, length_range=GENERATED_WORD_LENGTH_RANGE):
    words = []
    k = random.choice(k_range)
    random_text = generate_text()
    for _ in range(k):
        w_length = random.choice(length_range)
        w = random_text[:w_length]
        random_text = random_text[w_length:]
        words.append(w) 

    return words

def choose_words(msg, words_range=WORDS_FROM_MESSAGE_RANGE):
    words = re.compile('\w+').findall(msg)
    k = min(random.choice(WORDS_FROM_MESSAGE_RANGE), len(words))
    words = sorted(words, key=lambda x: len(x), reverse=True)
    return words[:k]

def generate_answer(msg):
    for _ in range(TRANSLATE_ATTEMPTS):
        chozen_words = choose_words(msg)
        generated_words = generate_words()
        all_words = chozen_words + generated_words
        random.shuffle(all_words)
        final_text = " ".join(all_words)
        print("  final_text", final_text)

        translated = Translator().translate(text=final_text, dest='ru', src='lb').text
        print("  translated", translated)

        if translated.lower()[0] not in CYRILLIC_SYMBOLS:
            continue 

        mutual = longest_substring_finder(final_text, translated)
        if len(mutual) < 10:
            return translated
    return "Истину знает только Бог."

def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message and update.message.text:  # your bot can receive updates without messages
            msg = update.message.text
            print("\nmsg", msg)

            if msg == '/start':
                update.message.reply_text("Задай вопрос. Познай ответ.")
                return

            answer = generate_answer(msg)
            translated = answer # Translator().translate(text=answer, dest='ru', src='en').text
            update.message.reply_text(translated)


if __name__ == '__main__':
    main()