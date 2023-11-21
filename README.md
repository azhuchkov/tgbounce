# tgbounce
Simple Telegram assistant

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

```console
$ brew install azhuchkov/tools/tgbounce
```
