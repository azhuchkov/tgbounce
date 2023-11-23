# tgbounce: Your Telegram Assistant
**tgbounce** is a versatile [Telegram](https://telegram.org) assistant designed to automate responses, log messages, 
click on buttons, and perform various actions based on your custom rules, acting on your behalf in Telegram chats.

## Application Model
`tgbounce` operates on **bounces**, rules created to respond to messages. Each bounce includes conditions and related 
actions. These conditions are appraised using matchers, ranging from basic field value comparisons to intricate 
expression evaluations. Explore the extensive message fields compatible with `tgbounce` in the 
[Telegram documentation](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1message.html).

### Available actions
Customize your reactions to messages with these reactions, which can be combined in any order:
- **reply(text, receiver=None)**: Sends a reply, optionally to a different receiver.
- **click(label)**: Clicks a button identified by its label.
- **mark_as_read()**: Marks a message as read.
- **exec(cmd)**: Executes a shell command. 

## Examples

### Automatic reply
Automate responses easily with `tgbounce`. For example, to reply to any private message starting with "Hello", 
use this configuration:
```json
{
  "bounces": [
    {
      "on": {
        "is_outgoing": false,
        "is_private": { "value":  "chat_id >= 0", "matcher": "expr" },
        "content.text.text": { "value": "^Hello.*$", "matcher": "regexp" }
      },
      "do": {
        "reply": ["Hi. Will respond to you in a minute."]
      }
    }
  ]
}

```

### Buttons handling
To click automatically on buttons, use the following config:
```json
{
  "bounces": [
    {
      "on": {
        "sender_id.user_id": 1234567890, 
        "content.text.text": { "value": "^Are you confirming .+?$", "matcher": "regexp" }
      },
      "do": {
        "click": ["Yes"],
        "mark_as_read": []
      }
    }
  ]
}
```

### Command execution
Here is the **bounce** that sends every text message to the Notification Center:
```json
{
  "on": {
    "is_outgoing": false,
    "has_text": {
      "value": "content.text != None and content.text.text != None",
      "matcher": "expr"
    }
  },
  "do": {
    "exec": ["jq -r .content.text.text | terminal-notifier -title 'Telegram' -subtitle 'Incoming Message'"]
  }
}
```

## Installation
Follow these steps to install tgbounce:

1. Install the latest version using Homebrew: 
```console
$ brew install --HEAD azhuchkov/tools/tgbounce
```

2. Create a directory for configuration files and copy the example files into it:
```console
$ mkdir -m 0700 ~/.tgbounce/ && \
  install -b -m 0600 /usr/local/opt/tgbounce/share/{config.ini,bounces.json} ~/.tgbounce/
```

3. Edit the main configuration file:
```console
$ vim ~/.tgbounce/config.ini
```

4. Start tgbounce manually to enter the required credentials:
```console
$ /usr/local/opt/tgbounce/libexec/bin/python3 /usr/local/opt/tgbounce/libexec/tgbounce.py
```

5. After configuration, start tgbounce as a service:
```console
$ brew services start tgbounce
```

## Troubleshooting
If you encounter issues, these commands can help:

- Check the service status:
```console
$ brew services info tgbounce
```

- Access the logs:
```console
$ less /usr/local/var/log/tgbounce.log
```

## Legal Information
`tgbounce` is licensed under the [GPLv3 License](LICENSE).