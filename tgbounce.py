from telegram.client import Telegram
import jq

import re
import json
import sys
import os
import configparser

MSG_SLCTR = jq.compile('''
.message
  |{
    id,
    chat_id,
    sender_id: .sender_id.user_id,
    is_outgoing,
    is_pinned,
    is_channel_post,
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
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def start(self):
        session = None

        with open(f'{self.root_dir}/rules.json') as f:
            json_tree = json.load(f)

            session = Session('main', json_tree['bounces'])

        cred = configparser.ConfigParser()
        cred.read(f'{self.root_dir}/cred.ini')

        conf = cred['main']

        tg = Telegram(
            api_id=int(conf['api_id']),
            api_hash=conf['api_hash'],
            phone=conf['phone_number'],
            use_message_database=False,
            use_secret_chats=False,
            database_encryption_key=conf['enc_key'],
            files_directory=f'{self.root_dir}/session/',
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

    @staticmethod
    def build(event, tg):
        return Message(tg, MSG_SLCTR.input_value(event).first())

    def __getitem__(self, item):
        return self.__msg[item]

    def mark_as_read(self):
        payload = {
            "chat_id": self.chat_id,
            "message_ids": [self.id],
            "force_read": True,
        }
        self.__tg.call_method("viewMessages", payload);

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

    def reply(self, text, receiver):
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
                    elif not re.fullmatch(value['value'], msg[attr]):
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
    data_path = sys.argv[1] if len(sys.argv) > 1 \
        else os.path.expanduser('~/.tgbounce/')

    app = TgBounce(data_path)
    app.start()
