import glob
import os
import subprocess
from configparser import ConfigParser

from Levenshtein import distance as levenshtein_distance

'''
Local Tesseract each product and grap picture with 'nutrition' label to nutrition_table_pic.txt
'''

config = ConfigParser()

config.read('config.ini')

output_path = config.get('main', 'output_path')
tesseract_config = config.get('main', 'tesseract_config')
target_word = config.get('main', 'target_word')
base_dir = config.get('main', 'base_dir')

try:
    with open(output_path, 'r') as f:
        rows = f.readlines()
        parsed_sku = set(row.split(':')[0] for row in rows)
except FileNotFoundError:
    print('FileNotFound, no parsed sku')
    parsed_sku = set()

# root_dir needs a trailing slash (i.e. /root/dir/)
for filename in glob.iglob(base_dir + '**/*.jpg', recursive=True):
    product = filename.split('/')[-2]
    pic_no = filename.split('/')[-1].split('.')[0]
    subfolder_name = os.path.dirname(os.path.normpath(filename))
    file_list = glob.glob(subfolder_name + '/*') 
    num_files = len(file_list)  # Get the count of files
    if int(pic_no) == (num_files-1) and product not in parsed_sku:
        try:
            result = subprocess.run(['tesseract',  filename, '-', '-l', 'eng+chi_tra', '--psm', '6', 
                    tesseract_config], capture_output=True, encoding='utf-8')
            result.check_returncode() # No exception means clean exit
            output_str = result.stdout.split(' ')
        except Exception as e:
            print(f"tesseract cannot parse product: {product}")
        else:
            for word in output_str:
                l_dist = levenshtein_distance(word.strip().lower(), target_word)
                if l_dist < 3:
                    with open(output_path, 'a+') as f:
                        match_word = word.replace('\n', '')
                        f.write(f"{product}:{pic_no}:{match_word}\n")
                        print(product, pic_no, match_word)
