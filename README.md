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
