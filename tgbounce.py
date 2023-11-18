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
    sessions = []

    with open(f'{self.root_dir}/rules.json') as f:
      json_tree = json.load(f)

      for name, subtree in json_tree['sessions'].items():
        sessions.append(Session(name, subtree))

    cred = configparser.ConfigParser()
    cred.read(f'{self.root_dir}/cred.ini')
    
    for session in sessions:
      conf = cred[session.name]

      tg = Telegram(
        api_id=conf['api_id'],
        api_hash=conf['api_hash'],
        phone=conf['phone_number'],
        use_message_database=False,
        use_secret_chats=False,
        database_encryption_key=conf['enc_key'],
        files_directory=
          f'{self.root_dir}/sessions/{session.name}',
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

    params={
      'chat_id': self.chat_id, 
      'message_id': self.id, 
      'payload': {
        '@type': 'callbackQueryPayloadData',
        'data': buttons[label]['data'],
      }
    }
    self.__tg.call_method('getCallbackQueryAnswer', params)

  def reply(self, text):
    raise Error('Not implemented')    

class Session:
  def __init__(self, name, rules):
    self.name = name
    self.rules = rules

  def on_message(self, msg):
    for rule in self.rules:
      for attr, value in rule['on'].items():
        if isinstance(value, dict):
          if value['matcher'] != 'regexp':
            raise Error(f'Unexpected matcher: {value}')
          elif not re.fullmatch(value['value'], msg[attr]):
            break
        elif value != msg[attr]:
          break
      else:
        for mname, args in rule['do'].items():
          method = getattr(msg, mname)
          if isinstance(args, dict):
            method(**args)
          else:
            method(*args)

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 \
      else os.path.expanduser('~/.tgbounce/')

    app = TgBounce(data_path)
    app.start()
 
   
