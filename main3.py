# Version 3

# 送信者になりすまして送信する。(chat:write:customize)
# プライベートで使用するには、アプリを追加する必要あり。

# メンションつけたい。。。
# 絵文字つけたい

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from deepl import deepl

APP_NAME = "DeepL Translator NEO"


# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# 'open_modal' という callback_id のショートカットをリッスン
@app.shortcut("test_deepl")
def open_modal(ack, shortcut, client):
    global trigger_id
    trigger_id=shortcut["trigger_id"]
    # ショートカットのリクエストを確認
    ack()
    # print(shortcut)
    # 組み込みのクライアントを使って views_open メソッドを呼び出す
    client.views_open(
        trigger_id=trigger_id,
        # モーダルで表示するシンプルなビューのペイロード
        view={
            "type": "modal",
            "callback_id": "run_translation",
            "title": {"type": "plain_text","text": APP_NAME},
            "close": {"type": "plain_text","text": "Close"},
            "submit": {"type": "plain_text","text": "Translate"},

            "blocks": [
                {
                    "type": "input",
                    "block_id": "text",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "content",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Type text to translate.\n翻訳する文を入力してください。"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Text",
                        "emoji": True
                    }
                },


                {
                    "type": "input",
                    "block_id": "lang",
                    "element": {
                        "type": "static_select",
                        "action_id": "content",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a language",
                            "emoji": True
                        },
                        "initial_option": {
                            "text": {
                                "type": "plain_text",
                                "text": "English:US:"
                            },
                            "value": "EN"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "English:US:",
                                    "emoji": True
                                },
                                "value": "EN"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "日本語:flag-jp:",
                                    "emoji": True
                                },
                                "value": "JA"
                            }
                        ],
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Translate to / 翻訳先の言語",
                        "emoji": True
                    }
                }
            ]
        }
    )


# 翻訳中＆結果表示
@app.view("run_translation")
def handle_submission(ack, body, client, view, logger):
    global text
    global lang
    global result_text
    global user_icon
    global user_name
    text = view["state"]["values"]["text"]["content"]["value"]
    lang = view["state"]["values"]["lang"]["content"]["selected_option"]["value"]
    user_id = body["user"]["id"]

    # 入力値を検証
    errors = {}
    if text is not None and len(text) <= 0:
        errors["text"] = "text section is empty"
    if len(errors) > 0:
        ack(response_action="errors", errors=errors)
        return
        
    # loading ...
    ack({
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text","text": APP_NAME},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "翻訳中... / Translating the text ..."
                    }
                },
            ]
        }    
    })
 
    # TextをDeepL APIを使用して翻訳する
    result_text = deepl(text, lang)

    # 翻訳結果の表示
    client.views_update(
        # ここにTryAgainに追加して、Sendボタンを作る
        # Text BoxにinitialOptionで入れておき、Sendでそのチャンネルに送信できたらいい。
        view_id=body["view"]["id"],
        view={
            "type": "modal",
            "callback_id": "send_to_channel",
            "title": {
                "type": "plain_text",
                "text": APP_NAME
            },
            "submit": {
                "type": "plain_text",
                "text": "Send Text"
            },
            "private_metadata": lang,
            "blocks": [
                {
                    # Source Text
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": text
                    }
                },
                {
                    # --------------
                    "type": "divider"
                },
                {
                    # Translated Text
                    "type": "input",
                    "block_id": "modified_text",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "text",
                        "multiline": True,
                        "initial_value": result_text
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Translated Text / 翻訳結果 : ",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "block_id": "channel",
                    "element": {
                        "type": "conversations_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Type a keyword / チャンネル名を入力",
                            "emoji": True
                        },
                        "filter": {
                            "include": [
                                "private",
                                "public"
                            ]
                        },
                        "action_id": "send_to"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Select a channel to send / 送信先のチャンネルを選択 : "
                    }
                },
                {
                    # --------------
                    "type": "divider"
                },
                {
                    # Try Again
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Retry Translation / 翻訳をやり直す",
                                "emoji": True
                            },
                            "style": "danger",
                            "value": "try_again",
                            "action_id": "try_again"
                        }
                    ]
                }
            ]
        }
    )

    # get profile with user_id
    response = client.users_info(
        user=user_id
    )

    user_icon = response["user"]["profile"]["image_48"]
    user_name = response["user"]["profile"]["display_name"]

    print(user_icon)
    print(user_name)






# Send Button
@app.view("send_to_channel")
def send_submission(ack, view, body, say, client):
    
    channel_id = view["state"]["values"]["channel"]["send_to"]["selected_conversation"]
    modified_text = view["state"]["values"]["modified_text"]["text"]["value"]
    
    errors = {}
    if modified_text is not None and len(modified_text) <= 0:
        errors["modified_text"] = "text section is empty"
    if "channel_id" not in locals():
        errors["channel"] = "A channel is not selected"
    if len(errors) > 0:
        print(errors)
        ack(response_action="errors", errors=errors)
        return
    

    print(user_name)
    print(user_icon)
    
    response = client.chat_postMessage(
        username=user_name,
        icon_url=user_icon,
        channel=channel_id,
        text=modified_text,
    )

    print(response)

    # say(channel=channel_id, text=modified_text)
    ack()
    
    

# Retry Translation
@app.action("try_again")
def try_again(ack, body, action, client):
    ack()
    client.views_update(
        # view_id を渡すこと
        view_id=body["view"]["id"],
        # 競合状態を防ぐためのビューの状態を示す文字列
        hash=body["view"]["hash"],
        # 更新後の blocks を含むビューのペイロード
        view={
            "type": "modal",
            "callback_id": "run_translation",
            "title": {"type": "plain_text","text": APP_NAME},
            "close": {"type": "plain_text","text": "Close"},
            "submit": {"type": "plain_text","text": "Translate"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "text",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "content",
                        "initial_value": text
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Text",
                        "emoji": True
                    }
                },


                {
                    "type": "input",
                    "block_id": "lang",
                    "element": {
                        "type": "static_select",
                        "action_id": "content",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a language",
                            "emoji": True
                        },
                        "initial_option": {
                            "text": {
                                "type": "plain_text",
                                "text": "English:US:"
                            },
                            "value": "EN"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "English:US:",
                                    "emoji": True
                                },
                                "value": "EN"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "日本語:flag-jp:",
                                    "emoji": True
                                },
                                "value": "JA"
                            }
                        ],
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Translate to ...",
                        "emoji": True
                    }
                }
            ]
        }
    )




# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()