# Open data (Food Information)

This repository contains tables with food information, including product details, categories, and nutrition facts.

## Table 1: Food Information Table (open_data/food_info.csv)
- **subcat**: Subcategory code
- **product_code**: Product code
- **product_brand**: Product brand
- **product_name**: Product name

Example data:
```
subcat,product_code,product_brand,product_name
04040201,BP_136717,壽桃牌,壽桃碗生麵皇(鮑雞味)
04040202,BP_116743,REEVA,牛肉味即食麵５包裝
```

## Table 2: Food Category Table (open_data/food_subcategory.csv)
- **subcat_name**: Subcategory name
- **subcat_code**: Subcategory code
- **sub_subcat_name**: Sub-subcategory name
- **sub_subcat_code**: Sub-subcategory code

Example data:
```
subcat_name,subcat_code,sub_subcat_name,sub_subcat_code
即食麵/飯、粉麵、意大利粉,04040200,杯麵、碗麵,04040201
即食麵/飯、粉麵、意大利粉,04040200,即食麵、公仔麵,04040202
```

## Table 3: Nutrition Table (open_data/nutrition_data.csv)
- **product**: Product code
- **hundred energy (kcal)**: Energy content per 100g (in kilocalories)
- **hundred protein (g)**: Protein content per 100g (in grams)
- **hundred total fat (g)**: Total fat content per 100g (in grams)
- **hundred saturated fat (g)**: Saturated fat content per 100g (in grams)
- **hundred trans fat (g)**: Trans fat content per 100g (in grams)
- **hundred carbohydrate (g)**: Carbohydrate content per 100g (in grams)
- **hundred dietary fiber (g)**: Dietary fiber content per 100g (in grams)
- **hundred sugars (g)**: Sugar content per 100g (in grams)
- **hundred sodium (mg)**: Sodium content per 100g (in milligrams)
- **per serve**: Serving size description
- **serve energy (kcal)**: Energy content per serving (in kilocalories)
- **serve protein (g)**: Protein content per serving (in grams)
- **serve total fat (g)**: Total fat content per serving (in grams)
- **serve saturated fat (g)**: Saturated fat content per serving (in grams)
- **serve trans fat (g)**: Trans fat content per serving (in grams)
- **serve carbohydrate (g)**: Carbohydrate content per serving (in grams)
- **serve dietary fiber (g)**: Dietary fiber content per serving (in grams)
- **serve sugars (g)**: Sugar content per serving (in grams)
- **serve sodium (mg)**: Sodium content per serving (in milligrams)

Example data:
```
product,hundred energy (kcal),hundred protein (g),hundred total fat (g),hundred saturated fat (g),hundred trans fat (g),hundred carbohydrate (g),hundred dietary fiber (g),hundred sugars (g),hundred sodium (mg),per serve,serve energy (kcal),serve protein (g),serve total fat (g),serve saturated fat (g),serve trans fat (g),serve carbohydrate (g),serve dietary fiber (g),serve sugars (g),serve sodium (mg)
BP_100191,,,,,,,,,,32.5 克 g,165,7.6,9.2,5.9,0.5,13,,13,109
BP_100303,47,0,0,0,0,11.4,,11.4,71,/,,,,,,,,,
BP_100339,25,0,0,0,0,6.2,,6.2,30,/,,,,,,,,,
```

# Source Code
## pnshk_scraper
Crawl parknshop website to get food products, categories, and photos.

1. pnshk_cat: spider to crawl parknshop food categories, to be used as input for the second spider.
2. pnshk_prod: crawl product info and photos by category.

Usage: 

To crawl parknshop food categories: `scrapy crawl pnshk_cat`

To crawl product info and photos by category: `scrapy crawl pnshk_prod`

## local_ocr
local tesseract ocr to identify nutrition info image

config:
1. tesseract_config: configuration path of local tesseract
2. target_word: default as 'nutrition', to be found in the image
3. base_dir: image directory
4. output_path: output result path (txt)

Usage: ```python local_tesseract.py```

## google_ocr
use google vision ai to parse nutrition info image

config:
1. base_dir: image directory
2. output_dir: output result directory
3. label_path: output result in local_ocr (txt)

Usage: ```python scan.py```

## parse
parse google vision ai results into csv table

config:
1. base_dir: output dirctory of google_ocr
2. output_dir: output result directory

Usage: ```python parse.py```

