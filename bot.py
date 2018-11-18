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
WORDS_FROM_MESSAGE_RANGE = range(2, 4)
GENERATED_WORD_LENGTH_RANGE = range(3, 6)

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

def generate_text(length):
    return ''.join(random.choices(CYRILLIC_SYMBOLS, k=length))

def generate_random_word(length_range=GENERATED_WORD_LENGTH_RANGE):
    return generate_text(random.choice(GENERATED_WORD_LENGTH_RANGE))

def generate_words(k=WORDS_TO_GENERATE_RANGE):
    return [generate_random_word() for _ in WORDS_TO_GENERATE_RANGE]

def choose_words(msg, words_range=WORDS_FROM_MESSAGE_RANGE):
    words = re.compile(r'\w+').findall(msg)
    k = min(random.choice(WORDS_FROM_MESSAGE_RANGE), len(words))
    words = sorted(words, key=lambda x: len(x), reverse=True)
    return words[:k]

def translate_to_english(msg):
    try:
        return Translator().translate(text=msg, dest='en').text
    except Exception as e:
        print(e)
        return None

def translate(msg, dest='ru', src='lb'):
    try:
        return Translator().translate(text=msg, dest=dest, src=src).text
    except Exception as e:
        print(e) 
        return None

def is_translation_valid(original, translated):
    if translated.lower()[0] not in CYRILLIC_SYMBOLS:
        return False 

    mutual = longest_substring_finder(original, translated)
    if len(mutual) > 10:
        print("  mutual:", mutual)
        return False

    return True
    
def generate_answer(msg):
    english = translate_to_english(msg)
    if english is None:
        return "Истину знает только Бог."

    print("  english:", english)
    try:
        for _ in range(TRANSLATE_ATTEMPTS):
            chozen_words = choose_words(english)
            generated_words = generate_words()
            all_words = chozen_words + generated_words
            random.shuffle(all_words)
            final_text = " ".join(all_words)
            print("  final_text:", final_text)
            translated = translate(final_text)
            print("  translated:", translated)

            if is_translation_valid(final_text, translated):
                return translated
            
    except Exception as e:
        print(e)
        pass
    
    return "Истину знает только Бог."
    

def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message and update.message.text:  # your bot can receive updates without messages
            msg = update.message.text
            username = update.message["chat"]["username"]
            name = "%s %s" % (update.message["chat"]["first_name"], update.message["chat"]["last_name"])
            print("\n@%s: %s" % (username if username else name, msg))

            if msg == '/start':
                update.message.reply_text("Задай вопрос. Познай ответ.")
                return

            answer = generate_answer(msg)
            translated = answer # Translator().translate(text=answer, dest='ru', src='en').text
            update.message.reply_text(translated)


if __name__ == '__main__':
    main()