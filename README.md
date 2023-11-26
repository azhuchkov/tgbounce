# tgbounce: Your Telegram Assistant
<img src="https://github.com/azhuchkov/tgbounce/blob/main/share/logo.png" alt="logo" align="right"/>

**tgbounce** is an advanced [Telegram](https://telegram.org) assistant, crafted to automate your chat interactions. 
It responds to messages, logs conversations, clicks buttons, and executes custom actions on your behalf, enhancing 
your Telegram experience with seamless efficiency.
<br clear="right"/>

## Application Model
`tgbounce` works with **bounces**, which are special rules set up to reply to messages. Each bounce has two parts: 
_conditions_ and _actions_. Conditions are the rules that decide when to do something, and actions are what `tgbounce`
does when those conditions are met. To check if a condition is true, `tgbounce` uses _matchers_. These can be simple 
checks or more complex evaluations. You can find out about the different kinds of fields `tgbounce` can work with 
by looking at the [Telegram documentation](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1message.html).

### Available actions
Specify your reactions to messages with the following actions, which can be used in any combination:
- **reply(text, receiver=None)**: Sends a reply, optionally to a different receiver.
- **click(label)**: Clicks a button identified by its label.
- **mark_as_read()**: Marks a message as read.
- **exec(cmd)**: Executes a shell command, passing the message to the process' STDIN in JSON format. 

## Examples

### Automatic reply
To reply to any private message starting with "Hello", use this configuration:
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
To click automatically on button "Yes" attached to special messages from a particular user, 
use the following config:
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
Here is the **bounce** that sends every text message to the [macOS Notification Center](https://support.apple.com/en-ge/guide/mac-help/mchl2fb1258f/14.0/mac/14.0):
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

1. Install the latest version using [Homebrew](https://brew.sh/): 
```console
$ brew install azhuchkov/tools/tgbounce
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

5. After entering credentials, exit (`Ctrl+C`) and then start tgbounce as a service:
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

- Reinstall the service, if any failures appear:
```console
$ brew uninstall tgbounce; brew install tgbounce; brew services restart tgbounce
```

## Signals
`tgbounce` supports the following signals: `SIGUSR1`, `SIGHUP`. The latter is used to reload the bounces configuration, 
and the former is used to notify the process about network changes for faster catch-up.

## Legal Information
`tgbounce` is licensed under the [GPLv3 License](LICENSE).
