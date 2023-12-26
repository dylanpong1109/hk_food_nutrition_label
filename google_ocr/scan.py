import glob
import os
import subprocess
from configparser import ConfigParser

from vision_ai import detect_text

'''
Google ocr to parse nutrition pic
'''

config = ConfigParser()

config.read('config.ini')

base_dir = config.get('main', 'base_dir')
output_dir = config.get('main', 'output_dir')
label_path = config.get('main', 'label_path')

with open(label_path, 'r') as f:
    text = f.readlines()

for line in text:
    product = line.strip().split(':')[0]
    pic_id = line.strip().split(':')[1]
    pic_path = base_dir + f'{product}/{pic_id}.jpg'
    result_path = output_dir + f'{product}_{pic_id}.csv'
    if not os.path.exists(result_path):
        print('running product: ', product, ' ', pic_id)
        # detect_text(pic_path, result_path)
