import os
import requests
import json
from urllib.parse import urlencode

DEEPL_AUTH_KEY = os.environ["DEEPL_AUTH_KEY"]

def deepl(text, lang):

  url = "https://api.deepl.com/v2/translate"

  paylaod = {
    "auth_key": DEEPL_AUTH_KEY,
    "text": text,
    "target_lang": lang
  }

  response = requests.post(url, data=paylaod)
  
  if(response.status_code != 200):
    log = "access failed."
    print(log)
    return log

  data = response.json()["translations"][0]
  result_text = data["text"]

  print(f"translated text: \n{result_text}")

  return result_text



# if __name__ == "__main__":


  # text = input("text: ")
  # choice = int(input("1: 日本語    2: English：　"))
  # deepl(text, choice)




# DeepL APIの出力例
# {
#   'translations': [{
#     'detected_source_language': 'EN',
#     'text': 'こんにちは'
#   }]
# }