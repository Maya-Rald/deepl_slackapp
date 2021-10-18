import os
import requests


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
