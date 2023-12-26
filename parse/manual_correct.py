import re

from Levenshtein import distance as levenshtein_distance

'''
Manually correct wrong ocr text
'''

def digit_gram_convert(text):
    ## min grap digit size 1 to 2 to avoid o/O -> 0 confusion
    digit_to_gram = r'([\d]{1,2}(?:\.[\d]{1,2})?\s?[890q])(?!.*(?:g|mg|kcal|kj|ml|毫克|克|千卡|千焦))'
    # if re.findall(digit_to_gram, text) != []:
    for word in re.findall(digit_to_gram, text):
        # last_9_index = word.rfind('9')
        converted_word = word.strip()[:-1] + 'g'

        # if last_9_index != -1:
        #     converted_word = word[:last_9_index] + 'g' + word[last_9_index + 1:]
        text = text.replace(word, converted_word)
    return text

def o_to_0(text):
    
    def replace_o_with_zero(match):
        print(match)
        return match.group(0).replace('O', '0').replace('o', '0')
    
    pattern = r'([\doO]{1,5}(?:\.[\doO]{1,2})?\s*)(?:g|克)'
    sodium_pattern = r'([\doO]{1,5}(?:\.[\doO]{1,2})?\s*)(?:mg|毫克)'
    energy_pattern = r'([\doO]{1,5}\s*)kcal'
    for i in [pattern, sodium_pattern, energy_pattern]:
        text = re.sub(i, replace_o_with_zero, text)
    return text

def digit_to_mg(text):
    text = text.replace('m9', 'mg')
    text = text.replace('m8', 'mg')
    return text

def levenshtein_correction(word):
    word_list = ['energy', 'protein', 'total', 'saturated', 
                'trans', 'fat', 'carbohydrate', 'dietary', 'fiber',
                'sugars', 'sodium', 'calcium', 'per']
    for matched_word in word_list:
        dist = len(matched_word) // 5 + 1
        # print(dist, matched_word)
        if levenshtein_distance(matched_word, word.lower()) <= dist:
            return matched_word
    return word

if __name__=="__main__":
    print(digit_gram_convert("STORAGE : Store in a cc data may differ from that sugars 1.19"))
    
    print(o_to_0('STORAGE : Store in a cc data may differ from that sugars 1.1g'))