import configparser
import json
import os
import re
import sys
import logging
import time
import datetime

from telegram.client import Telegram


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
            bounces = [Bounce.parse(b) for b in json_tree['bounces']]

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

        def on_message(event):
            try:
                for bounce in bounces:
                    bounce.on_message(Message(tg, event['message']))
            except:
                logging.error("Error during message handling", exc_info=True)

        tg.add_message_handler(on_message)
        tg.idle()


class Message:
    def __init__(self, tg, msg):
        self.__tg = tg
        self.__msg = msg
        self.__dict__.update(msg)

    def __getitem__(self, item):
        return self.__msg[item]

    def mark_as_read(self):
        payload = {
            "chat_id": self.chat_id,
            "message_ids": [self.id],
            "force_read": True,
        }
        self.__tg.call_method("viewMessages", payload)

    def click(self, label):
        for row in self.__msg['reply_markup']['rows']:
            for button in row:
                if button['text'] == label:
                    params = {
                        'chat_id': self.chat_id,
                        'message_id': self.id,
                        'payload': {
                            '@type': 'callbackQueryPayloadData',
                            'data': button['type']['data'],
                        }
                    }
                    self.__tg.call_method('getCallbackQueryAnswer', params)
                    return
        raise Exception(f'Button not found: {label}')

    def log(self):
        logging.info(f'MESSAGE:\n%s' % json.dumps(self.__msg, indent=2, ensure_ascii=False))

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


class EqualityMatcher:
    def __init__(self, expected):
        self.expected = expected

    def match(self, actual):
        return self.expected == actual

    def __repr__(self):
        return f'== {self.expected}'


class RegexpMatcher:
    def __init__(self, regexp):
        self.regexp = regexp

    def match(self, actual):
        return actual is not None and re.fullmatch(self.regexp, actual)

    def __repr__(self):
        return f'~ {self.regexp}'


def obj_attr(obj, attr_path):
    """
    Tries to get nested attribute of an object as well as nested key of a dict.
    :param obj: Object to get attribute from.
    :param attr_path: Attribute name or path to it, e.g. 'a.b.c'.
    :return: Attribute value or None if attribute doesn't exist.
    """
    try:
        for attr in attr_path.split('.'):
            if isinstance(obj, dict):
                obj = obj[attr]
            else:
                obj = getattr(obj, attr)
        return obj
    except (AttributeError, KeyError, TypeError):
        return None


class FieldCondition:
    def __init__(self, attr_path, matcher):
        self.attr_path = attr_path
        self.matcher = matcher

    def is_fulfilled(self, msg):
        return self.matcher.match(obj_attr(msg, self.attr_path))

    def __repr__(self):
        return f'{self.attr_path} {self.matcher}'


class ExpressionCondition:
    def __init__(self, expression):
        self.expression = expression

    def is_fulfilled(self, msg):
        return eval(self.expression, {'time': time, 'datetime': datetime}, msg)

    def __repr__(self):
        return f'{self.expression}'


class Bounce:
    def __init__(self, conditions, action):
        self.conditions = conditions
        self.action = action

    def __str__(self):
        return f'{self.conditions} -> {self.action}'

    def on_message(self, msg):
        if all(cond.is_fulfilled(msg) for cond in self.conditions):
            logging.info(f'MATCH: {msg.id} -- {self.conditions}')
            self.action(msg)

    @staticmethod
    def parse(json_tree):
        conds = []
        for attr, matcher in json_tree['on'].items():
            if isinstance(matcher, dict):
                matcher_value = matcher['value']

                if matcher['matcher'] in ('regexp', 'regex'):
                    conds.append(FieldCondition(attr, RegexpMatcher(matcher_value)))

                elif matcher['matcher'] in ('eq', 'equal', 'equals'):
                    conds.append(FieldCondition(attr, EqualityMatcher(matcher_value)))

                elif matcher['matcher'] in ('expr', 'expression'):
                    conds.append(ExpressionCondition(matcher_value))

                else:
                    raise Exception(f'Unexpected matcher: {matcher}')
            else:
                conds.append(FieldCondition(attr, EqualityMatcher(matcher)))

        do = json_tree['do']

        supported_actions = [method for method in dir(Message) if not method.startswith('_')]

        def check_supported(action):
            if action not in supported_actions:
                raise Exception(f'Unexpected action: {action}. Supported: {supported_actions}')

        if isinstance(do, str):
            check_supported(do)
        else:
            for method in do:
                check_supported(method)

        def action(msg):
            if isinstance(do, str):
                msg(do, [])
            else:
                for method, args in do.items():
                    msg(method, args)

        return Bounce(conds, action)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    profile = sys.argv[1] if len(sys.argv) > 1 else 'DEFAULT'

    config_path = sys.argv[2] if len(sys.argv) > 2 \
        else os.path.expanduser('~/.tgbounce/config.ini')

    app = TgBounce(config_path, profile)
    app.start()
