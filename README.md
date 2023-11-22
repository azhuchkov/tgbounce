# tgbounce: Your Telegram Assistant
**tgbounce** is a versatile [Telegram](https://telegram.org) assistant designed to automate responses, log messages, click on buttons, and perform various actions based on your custom rules, acting on your behalf in Telegram chats.

## Example configuration
Automate responses easily with tgbounce. For example, to reply to any private message starting with "Hello", use this configuration:
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

## Message object
Explore the wide range of message fields tgbounce can interact with in the [Telegram documentation](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1message.html).

## Available actions
Customize your reactions to messages with these actions in a `do` block:
```
reply(text, receiver=0): Send a reply to the sender.
click(label): Click on a specified button or link.
log(path=None): Log the message to a file.
mark_as_read(): Mark the message as read.
notify(text, subtitle=''): Send a notification with optional subtitle.
```
