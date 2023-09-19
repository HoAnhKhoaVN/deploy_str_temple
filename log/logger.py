import logging
from datetime import datetime

def setup_logger(log_file='log/app.log'):
    cur_time = datetime.now()
    str_cur_time = cur_time.strftime("%Y_%m_%d")
    logging.basicConfig(
        filename=f'log/{str_cur_time}.log', level=logging.DEBUG,
        format='[%(asctime)s: %(filename)s] - %(levelname)s - %(message)s',
        encoding='utf-8'
    )