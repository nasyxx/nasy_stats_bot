#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
Life's pathetic, have fun ("▔□▔)/hi~♡ Nasy.

Excited without bugs::

    |             *         *
    |                  .                .
    |           .
    |     *                      ,
    |                   .
    |
    |                               *
    |          |\___/|
    |          )    -(             .              ·
    |         =\ -   /=
    |           )===(       *
    |          /   - \
    |          |-    |
    |         /   -   \     0.|.0
    |  NASY___\__( (__/_____(\=/)__+1s____________
    |  ______|____) )______|______|______|______|_
    |  ___|______( (____|______|______|______|____
    |  ______|____\_|______|______|______|______|_
    |  ___|______|______|______|______|______|____
    |  ______|______|______|______|______|______|_
    |  ___|______|______|______|______|______|____

author   : Nasy https://nasy.moe
date     : Feb 12, 2020
email    : Nasy <nasyxx+python@gmail.com>
filename : bot.py
project  : nasy_stats_bot
license  : GPL-3.0+

At pick'd leisure
  Which shall be shortly, single I'll resolve you,
Which to you shall seem probable, of every
  These happen'd accidents
                          -- The Tempest
"""
# Standard Library
import shelve
import time
from collections import Counter

# Telegram
from telegram import Message
from telegram.ext import (
    BaseFilter,
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater
)
from telegram.update import Update

# Others
import pendulum

# Config
from config import CONFIG

# Types
from typing import NamedTuple, Set


class NoToken(Exception):
    """No Token Exception."""


TOKEN = CONFIG.get("TOKEN", "")
if not TOKEN:
    raise NoToken
DB_PATH = CONFIG.get("DB_PATH", "./bot.db")
TZ = CONFIG.get("TZ", "")

Time = pendulum.DateTime
Msg = NamedTuple(
    "Msg", [("id", int), ("time", Time), ("type", str), ("user", int)]
)


def get_user(msg: Msg) -> int:
    """Return user of a message."""
    return msg.user


def memed_groups() -> Set[int]:
    """Memoried groups."""
    with shelve.open(DB_PATH) as bot_db:
        return bot_db.get("groups", set())


def mem_group(chat_id: int) -> None:
    """Memory and stat the `chat_id` group."""
    with shelve.open(DB_PATH) as bot_db:
        bot_db["groups"] = (lambda groups: groups.add(chat_id) or groups)(
            bot_db.get("groups", set())
        )


def start(update: Update, context: CallbackContext) -> None:
    """Start command handle."""
    (lambda chats: time.sleep(3) or chats[0].delete())(
        (
            lambda in_group: (
                update.message.reply_markdown(
                    (
                        "Already started!"
                        if update.message.chat.id in memed_groups()
                        else "Start"
                    )
                    if in_group
                    else "Not in a group.",
                    quote=False,
                ),
                mem_group(update.message.chat.id) if in_group else None,
            )
        )("group" in update.message.chat.type)
    )


def mem_message(update: Update, context: CallbackContext) -> None:
    """Memory message to stat."""
    with shelve.open(DB_PATH) as bot_db:
        bot_db[str(update.message.chat.id)] = (
            lambda chat: chat.add(
                Msg(
                    update.message.message_id,
                    pendulum.now(TZ),
                    update.message.photo and "photo" or "other",
                    update.message.from_user.id,
                )
            )
            or chat
        )(bot_db.get(str(update.message.chat.id), set()))


def photo_stat(update: Update, context: CallbackContext) -> None:
    """Photo stat."""
    with shelve.open(DB_PATH) as bot_db:
        update.message.reply_markdown(
            "\n".join(
                map(
                    lambda user_c: " -- ".join(
                        (
                            (
                                lambda user: user.first_name
                                or user.last_name
                                or user.username
                                or "???"
                            )(
                                context.bot.get_chat_member(
                                    update.message.chat.id, user_c[0]
                                ).user
                            ),
                            str(user_c[1]),
                        )
                    ),
                    Counter(
                        map(
                            get_user,
                            filter(
                                lambda msg: msg.type == "photo"
                                and msg.time.date()
                                > pendulum.now().date().add(days=-7),
                                bot_db.get(str(update.message.chat.id), set()),
                            ),
                        )
                    ).most_common(10),
                ),
            ),
            quote=False,
        )


if __name__ == "__main__":
    bot = Updater(token=TOKEN, use_context=True)
    bot.dispatcher.add_handler(CommandHandler("start", start))
    bot.dispatcher.add_handler(CommandHandler("stat", photo_stat))
    bot.dispatcher.add_handler(MessageHandler(Filters.all, mem_message))
    bot.start_polling()
