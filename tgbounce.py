import configparser
import json
import os
import re
import sys

import jq
from telegram.client import Telegram

MSG_SLCTR = jq.compile('''
.message
  |{
    id,
    chat_id,
    sender_id: .sender_id.user_id,
    is_outgoing,
    is_pinned,
    is_channel_post,
    message_thread_id,
    ttl,
    text: .content.text.text,
    reply_markup}''')

BTN_SLCTR = jq.compile('''
[
  .reply_markup.rows[]
    | .[]
    | { label: .text, data: .type.data }
]
  | map({ (.label|tostring):. })
  | add''')


class TgBounce:
    def __init__(self, config_path, profile):
        self.config_path = config_path
        self.profile = profile

    def start(self):
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path)

        config = config_parser[self.profile]

        def resolve_path(path):
            return path if os.path.isabs(path) \
                else os.path.dirname(os.path.abspath(self.config_path)) + '/' + path

        with open(resolve_path(config['bounces_file'])) as f:
            json_tree = json.load(f)
            session = Session('main', json_tree['bounces'])

        tg = Telegram(
            api_id=int(config['api_id']),
            api_hash=config['api_hash'],
            phone=config['phone_number'],
            use_message_database=False,
            use_secret_chats=False,
            database_encryption_key=config['enc_key'],
            files_directory=resolve_path(config['data_dir'])
        )
        tg.login()
        tg.add_message_handler(
            lambda e: session.on_message(Message.build(e, tg)))
        tg.idle()


class Message:
    def __init__(self, tg, msg):
        self.__tg = tg
        self.__msg = msg
        self.__dict__.update(msg)
        self.__dict__['is_private'] = msg['chat_id'] >= 0

    @staticmethod
    def build(event, tg):
        return Message(tg, MSG_SLCTR.input_value(event).first())

    def __getitem__(self, item):
        return self.__dict__[item]

    def mark_as_read(self):
        payload = {
            "chat_id": self.chat_id,
            "message_ids": [self.id],
            "force_read": True,
        }
        self.__tg.call_method("viewMessages", payload)

    def click(self, label):
        buttons = BTN_SLCTR.input_value(self.__msg).first()

        params = {
            'chat_id': self.chat_id,
            'message_id': self.id,
            'payload': {
                '@type': 'callbackQueryPayloadData',
                'data': buttons[label]['data'],
            }
        }
        self.__tg.call_method('getCallbackQueryAnswer', params)

    def log(self):
        print(json.dumps(self.__msg, indent=2, ensure_ascii=False))

    def reply(self, text, receiver=0):
        self.__tg.send_message(receiver or self.chat_id, text)

    def __call__(self, method, args):
        fn = getattr(self, method)
        if isinstance(args, dict):
            fn(**args)
        elif isinstance(args, list):
            fn(*args)
        else:
            fn(args)


class Session:
    def __init__(self, name, rules):
        self.name = name
        self.rules = rules

    def on_message(self, msg):
        for rule in self.rules:
            for attr, value in rule['on'].items():
                if isinstance(value, dict):
                    if value['matcher'] != 'regexp':
                        raise Exception(f'Unexpected matcher: {value}')
                    elif msg[attr] is None or not re.fullmatch(value['value'], msg[attr]):
                        break
                elif value != msg[attr]:
                    break
            else:
                do = rule['do']
                if isinstance(do, str):
                    msg(do, [])
                else:
                    for method, args in do.items():
                        msg(method, args)


if __name__ == '__main__':
    profile = sys.argv[1] if len(sys.argv) > 1 else 'DEFAULT'

    config_path = sys.argv[2] if len(sys.argv) > 2 \
        else os.path.expanduser('~/.tgbounce/config.ini')

    app = TgBounce(config_path, profile)
    app.start()
