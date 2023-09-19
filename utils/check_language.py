import re

def is_han_nom(
    text: str
)-> bool:
    '''
    Hint: https://stackoverflow.com/questions/34587346/python-check-if-a-string-contains-chinese-character
    '''
    return len(re.findall(r'[\u4e00-\u9fff]+', text)) != 0

if __name__ == '__main__':
    text ='蛇龍動易'
    # text = 'NAMCAO'
    print(is_han_nom(text))