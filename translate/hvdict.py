import json
import time
import requests
from typing import List, Dict, Text, Any
import string
from log.logger import setup_logger, logging
setup_logger()

def merge_results(
    result: List[Dict[Text, Any]]
)-> Text:
    han_nom_2_quoc_ngu = []
    for r in result:
        _r = r.get('o', None)
        if _r:
            han_nom_2_quoc_ngu.append(_r[0].capitalize())
    han_nom_2_quoc_ngu = ' '.join(han_nom_2_quoc_ngu)
    return han_nom_2_quoc_ngu
    

def hvdic_translate(text):
    def is_nom_text(result):
        for phonetics_dict in result:
            if phonetics_dict['t'] == 3 and len(phonetics_dict['o']) <= 0:
                return True
        return False
    
    url = 'https://hvdic.thivien.net/transcript-query.json.php'
    headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' }

    # Request phonetics for Hán Việt (lang=1) first, if the response result is not
    # Hán Việt (contains blank lists) => Request phonetics for Nôm (lang=3)
    for lang in [1, 3]:
        payload = f'mode=trans&lang={lang}&input={text}'
        response = requests.request('POST', url, headers=headers, data=payload.encode())
        time.sleep(0.1)

        try:
            result = json.loads(response.text)['result']
        except:
            logging.error(f'{text}: {response.text}')
            result = {}
        if not is_nom_text(result): break

    # Merge the result
    han_nom_2_quoc_ngu = merge_results(result)

    return han_nom_2_quoc_ngu

if __name__ == '__main__':
    text ='蛇龍動易'
    print(hvdic_translate(text))