#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
# Coded with ❤️ by Neranjana Prasad (@NandiyaLive)

# Telegram
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
import requests
from telegram import Bot

# For features
from instaloader import Instaloader, Profile, Post
import sys
import shutil
import glob
import os
import zipfile
import pathlib

bot_token = "1290227041:AAHf-shTSNu-RieRT0T1qUnvCOXEnDeCcME"
bot = Bot(token=bot_token)


def start(update, context):
    user = context.bot.get_chat_member(chat_id='@MBNChat', user_id=update.message.chat_id)
    status = user["status"]
    if(status == 'left'):
        context.bot.send_message(chat_id=update.message.chat_id,text="To use to bot you need to be a member of @MBNUpdates and @MBNChat in order to stay updated with the latest developments.")
        return
    else :
        context.bot.send_message(chat_id=update.message.chat_id,
                                    text="Hello beta tester, you can early access @NandiyaLive's projects' new features through this.\n\nUse /now command to see what are the features curruntly running on this bot and know how to use them.\n\nJoin @MBNUpdates for more info.", parse_mode=telegram.ParseMode.HTML)


def now(update, context):
    update.message.reply_text('''These features are not yet ready for production, so there will be some errors. If you are having any, please send a message to @MDNChat.\n<b>Curruntly running :</b>\nA feature for @xIGDLBot to bulk download posts from instagram as a zip file.\n<b>Usage :</b>\n/feed [username] - Download all posts from the username’s profile as a zip file.''', parse_mode=telegram.ParseMode.HTML)


def echo(update, context):
    update.message.reply_text('Please read /now')


def feed(update, context):
    user = context.bot.get_chat_member(chat_id='@MBNChat', user_id=update.message.chat_id)
    status = user["status"]
    if(status == 'left'):
        context.bot.send_message(chat_id=update.message.chat_id,text="To use to bot you need to be a member of @MBNUpdates and @MBNChat in order to stay updated with the latest developments.")
        return
    else :
        fullmsg = update.message.text

        if fullmsg == "/feed":
            update.message.reply_text(
                '/feed [instagram username]\nPlease read /help')
        else:
            msg = fullmsg.replace("/feed ", "")

            if "@" in msg.lower():
                query = msg.replace("@", "")
            else:
                query = msg

        L = Instaloader(dirname_pattern=query, download_comments=False,
                        download_video_thumbnails=False, save_metadata=False, download_geotags=True, compress_json=True, post_metadata_txt_pattern=None, storyitem_metadata_txt_pattern=None)
        profile = Profile.from_username(L.context, query)

        media = profile.mediacount
        update.message.reply_text("Cooking your request 👨‍🍳\nProfile : " + query + "\nMedia Count : " + str(media) +
                                "\nThis may take longer, take a nap I can handle this without you.")

        posts = profile.get_posts()
        try:
            L.posts_download_loop(posts, query)
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat_id, text="<b>ERROR\n"+str(
                e), parse_mode=telegram.ParseMode.HTML)
            return

        update.message.reply_text("Download Completed.\n🗄 Archiving files...")

        zf = zipfile.ZipFile(f"{query}.zip", "w")
        for dirname, subdirs, files in os.walk(query):
            zf.write(query)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()

        update.message.reply_text("Uploading to Telegram...")

        for zip_file in glob.glob("*.zip"):
            context.bot.send_document(chat_id=update.message.chat_id,
                                    document=open(zip_file, 'rb'))

        try:
            shutil.rmtree(query)
            os.remove(f"{query}.zip")
        except Exception:
            pass


def main():
    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(CommandHandler("now", now, run_async=True))
    dp.add_handler(CommandHandler("feed", feed, run_async=True))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
