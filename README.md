# tgbounce
Simple Telegram assistant. Automatically replies, logs, clicks, etc. according to your rules and on your behalf.

## Example configuration
To automatically respond to any private message that starts with `Hello`, the following configuration can be applied:
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
Install the latest version using Homebrew:
```console
$ brew install --HEAD azhuchkov/tools/tgbounce
```

Copy example configuration files:
```console
$ mkdir -m 0700 ~/.tgbounce/ && install -b -m 0600 /usr/local/opt/tgbounce/share/{config.ini,bounces.json} ~/.tgbounce/
```

Edit the main configuration file filling up the gaps:
```console
$ vim ~/.tgbounce/config.ini
```

Start the service manually to enter required credentials:
```console
$ /usr/bin/env /usr/local/opt/tgbounce/libexec/bin/python3 /usr/local/opt/tgbounce/libexec/tgbounce.py
```

Now it's all set - hit `CTRL+C`, edit `~/.tgbounce/bounces.json` and start the service again using Homebrew:
```console
$ brew services start tgbounce
```

## Troubleshooting
To view service status use:
```console
$ brew services info tgbounce
```

To view logs:
```console
$ less /usr/local/var/log/tgbounce.log
```

## Message object
To view all the available message fields discover [Telegram documentation](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1message.html).

## Available actions
The following actions can be used in a `do` block as a reaction to the matched message:
```
reply(text, receiver=0)

click(label)

log(path=None)

mark_as_read()

notify(text, subtitle='')
```
