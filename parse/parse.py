import os
import re
import ast
import csv
import pandas as pd
from configparser import ConfigParser

from Levenshtein import distance as levenshtein_distance

from manual_correct import *

'''
Pipeline to parse google ocr result into csv table
'''

nutrition_list = ['product', 'energy', 'protein', 'total fat', 'saturated fat', 
                'trans fat', 'carbohydrate', 'dietary fiber',
                'sugars', 'sodium']
column_list = ['product', 'hundred energy', 'hundred protein', 'hundred total fat', 
                'hundred saturated fat', 'hundred trans fat', 'hundred carbohydrate', 
                'hundred dietary fiber', 'hundred sugars', 'hundred sodium', 'per serve',
                'serve energy', 'serve protein', 'serve total fat', 'serve saturated fat', 
                'serve trans fat', 'serve carbohydrate', 'serve dietary fiber',
                'serve sugars', 'serve sodium']

def parse_result(raw_csv, interim_csv):

    df = pd.read_csv(raw_csv)
    # remove first row (whole pic text)
    df = df.iloc[1:,:]
    # Convert 'coordinate' column from string type to tuple type
    df['bottomleft'] = df['bottomleft'].apply(ast.literal_eval)
    df['topleft'] = df['topleft'].apply(ast.literal_eval)

    # Extract y-coordinates from 'coordinate' column
    df['x'] = df['bottomleft'].apply(lambda x: x[0])
    df['y'] = df['bottomleft'].apply(lambda x: x[1])
    df['top_y'] = df['topleft'].apply(lambda x: x[1])
    df['font_height'] = df['top_y'] - df['y']

    # Sort dataframe by y-coordinates
    df = df.sort_values(['y'])

    df['group'] = 0 # Initialize the 'group' column
    current_group = 0
    min_y = df.iloc[0]['y'] # Initialize the minimum 'y' value

    # Iterate through the sorted 'y' values
    for i in range(1, len(df)):
        if df.iloc[i]['y'] - min_y > df.iloc[i]['font_height'] * 3/4: # Check if the difference is greater than 10
            current_group += 1 # Increment the group number
            min_y = df.iloc[i]['y'] # Update the minimum 'y' value
        df.iloc[i, df.columns.get_loc('group')] = current_group # Assign the group number
        
    # # Create a new column 'group' to indicate the group of rows based on the difference of y-coordinate
    # df['group'] = (df['y'].diff() > 10).cumsum()

    # Sort dataframe by y-coordinates
    df = df.sort_values(['group', 'x'])

    df['description'] = df['description'].apply(levenshtein_correction)

    # Group by 'group' column, then combine 'description' and 'coordinate' column
    df_grouped = df.groupby('group').agg({
        'description': lambda x: ' '.join(x),
        'bottomleft': lambda x: tuple(x)
    }).reset_index(drop=True)
    df_grouped = df_grouped.dropna(subset=['description'])
    df_grouped = df_grouped[df_grouped.description!='']
    
    df_grouped.to_csv(interim_csv, index=False)
    return df_grouped

def identify_col(text):
    pre_serve = r'per\s*serving'
    per_100 = r'per\s*100'
    if re.search(per_100 + r'.*' + pre_serve, text):
        print('identify hundred_left')
        return 'hundred_left'
    elif re.search(pre_serve + r'.*' + per_100, text):
        print('identify hundred_right')
        return 'hundred_right'
    elif re.search(per_100, text):
        print('identify hundred')
        return 'hundred'
    elif re.search(pre_serve, text):
        print('identify serve')
        return 'serve'
    else:
        print('identify none')
        return None

def grep_val(col_type, pattern, text):
    val = re.findall(pattern, text)
    if val == []:
        return ('', '')
    else:
        if col_type == 'hundred':
            return (val[0].strip(), '')
        elif col_type == 'hundred_left':
            return (val[0].strip(), val[-1].strip())
        elif col_type == 'hundred_right':
            return (val[-1].strip(), val[0].strip())
        elif col_type == 'serve':
            return ('', val[0].strip())

def stored_info(file, input_list, header = False):
    with open(file, 'a+') as f:   
        writer = csv.DictWriter(f, fieldnames = column_list)
        if header:
            writer.writeheader()
        writer.writerows(input_list)

def parse_table(df, product):
    nutrition_dict = dict()
    nutrition_dict['product'] = product
    kj_to_kcal = 0.239
    pattern = r'([\d]{1,5}(?:\.[\d]{1,2})?\s*)(?:g|克)'
    sodium_pattern = r'([\d]{1,5}(?:\.[\d]{1,2})?\s*)(?:mg|毫克)'
    # energy_pattern = r'([\d]{1,3}(?:kcal|kj))'
    kcal_pattern = r'([\d]{1,5}(?:\.[\d]{1,2})?\s*)(?:kcal|千卡)'
    kj_pattern = r'([\d]{1,5}(?:\.[\d]{1,2})?\s*)(?:kj|千焦)'
    check_serving_size = r'serving\s*size\s*'
    serving_size = r'(\d+\.?\d*\s?(?:毫克|克|毫升|升)?\s?(?:g|mg|ml|l))'
    check_flag = False
    col_type = None
    for text in df['description']:
        text = text.lower()
        print('text: ', text)

        if re.search(check_serving_size, text) and nutrition_dict.get('per serve') is None:
            if re.findall(serving_size, text):
                nutrition_dict['per serve'] = re.findall(serving_size, text)[0]
            else:
                nutrition_dict['per serve'] = ''

        if not col_type:
            col_type = identify_col(text)
            print('col_type', col_type)
        else:
            for nutrition in nutrition_list:
                if nutrition in text and nutrition not in nutrition_dict:
                    _, nutrition, after_nutrition = text.partition(nutrition)
                    print('nutrition', nutrition)
                    if nutrition == 'energy':
                        after_nutrition = o_to_0(after_nutrition) 
                        energy_val = grep_val(col_type, kcal_pattern, after_nutrition)
                        if energy_val != ('', ''):
                            nutrition_dict[f'hundred {nutrition}'], nutrition_dict[f'serve {nutrition}'] = energy_val
                        else:
                            energy_val = grep_val(col_type, kj_pattern, after_nutrition)
                            if energy_val != ('', ''):
                                try:
                                    nutrition_dict[f'hundred {nutrition}'] = float(energy_val[0]) * kj_to_kcal
                                except ValueError:
                                    nutrition_dict[f'hundred {nutrition}'] = ''
                                try:
                                    nutrition_dict[f'serve {nutrition}'] = float(energy_val[1]) * kj_to_kcal
                                except ValueError:
                                    nutrition_dict[f'serve {nutrition}'] = ''
                            else:
                                nutrition_dict[f'hundred {nutrition}'] = ''
                                nutrition_dict[f'serve {nutrition}'] = ''
                        # nutrition_dict[nutrition] = energy_val[0].strip() if col_type != 'hundred_right' else energy_val[-1].strip()
                    elif nutrition == 'sodium':
                        after_nutrition = digit_to_mg(after_nutrition) 
                        after_nutrition = o_to_0(after_nutrition) 
                        nutrition_dict[f'hundred {nutrition}'], nutrition_dict[f'serve {nutrition}'] = grep_val(col_type, sodium_pattern, after_nutrition)
                        # nutrition_dict[nutrition] = nutrition_val[0].strip() if col_type != 'hundred_right' else nutrition_val[-1].strip()
                    else:
                        after_nutrition = digit_gram_convert(after_nutrition)
                        after_nutrition = o_to_0(after_nutrition) 
                        nutrition_dict[f'hundred {nutrition}'], nutrition_dict[f'serve {nutrition}'] = grep_val(col_type, pattern, after_nutrition)
                        # nutrition_dict[nutrition] = nutrition_val[0].strip() if col_type != 'hundred_right' else nutrition_val[-1].strip()
    print(nutrition_dict)
    return nutrition_dict


def main(base_dir, output_csv):
    raw_path = base_dir + '/raw'
    input_list = []
    for idx, product_pic in enumerate(sorted(os.listdir(raw_path))):
        raw_csv = os.path.join(raw_path, product_pic)
        product = product_pic.split('.')[0][:-2]
        print('raw_csv', raw_csv)
        interim_path = base_dir + '/interim_v2/'
        if not os.path.exists(interim_path):
            os.makedirs(interim_path)
        interim_csv = interim_path + raw_csv.split('/')[-1].split('.')[0] + '_interim' + '.csv'
        if not os.path.exists(interim_csv):
            df = parse_result(raw_csv, interim_csv)
            nutrition_dict = parse_table(df, product)
            input_list.append(nutrition_dict)

    if os.path.exists(output_csv):
        stored_info(output_csv, input_list)
    else:
        stored_info(output_csv, input_list, header=True)

if __name__=="__main__":

    config = ConfigParser()

    config.read('config.ini')

    base_dir = config.get('main', 'base_dir')
    output_csv = config.get('main', 'output_csv')
    main(base_dir, output_csv)