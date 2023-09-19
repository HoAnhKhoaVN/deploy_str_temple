import json
import time
import requests
from typing import Text

ERR_TRANSLATE_STR = 'Cannot translate this text.'

def postproces_hcmus_translation(
    text: Text
)-> Text:
    lst_text = text.split()
    lst_capitalize_text = list(map(lambda x: x.capitalize(), lst_text))
    res = ' '.join(lst_capitalize_text) 
    return res

def hcmus_translate(
    text: Text
    ):
    url = ' https://api.clc.hcmus.edu.vn/nom_translation/90/1'
    response = requests.request('POST', url, data={'nom_text': text})
    time.sleep(0.3)

    try:
        result = json.loads(response.text)['sentences']
        result = result[0][0]['pair']['modern_text']

        # region post processing
        result = postproces_hcmus_translation(text = result)
        # endregion 
        return result
    except:
        print(f'[ERR] "{text}": {response.text}')
        return ERR_TRANSLATE_STR

if __name__ == '__main__':
    text ='越南'
    print(hcmus_translate(text))