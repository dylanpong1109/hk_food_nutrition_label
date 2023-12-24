from pathlib import Path
import xmltodict, json

import scrapy

class PnshkCatSpider(scrapy.Spider):
    name = "pnshk_cat"
    payload={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/json,image/avif,image/webp,image/apng'
    }

    def extract_response(self, response):
        try:
            content = json.loads(response.body)
            self.logger.info('json extract response')
            # self.logger.info(content)
            cat_list = content.get('categories')
            allSubcategories = cat_list[0].get('allSubcategories')

        except:
            content = xmltodict.parse(response.body)
            # print(content)
            self.logger.info('xml extract response')
            # self.logger.info(content)
            cat_list = content.get('categoryList')
            cat_list = cat_list.get('categories')
            allSubcategories = cat_list.get('allSubcategories')
            # print(allSubcategories)
        return allSubcategories

    def start_requests(self):
        urls = [
            "https://api.pns.hk/api/v2/pnshk/categories/multi/04000000?lang=zh_HK&curr=HKD"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.main_cat, headers=self.payload)

    def main_cat(self, response):
        # print(response.body)
        cat_list = self.extract_response(response)

        for subcat in cat_list:
            subcat_list = subcat.get('allSubcategories')
            for subcat_item in subcat_list:
                subcat_code = subcat_item.get('code')
                subcat_name = subcat_item.get('name')
                self.logger.info(f'Current subcat_code: {subcat_code}')
                url = f'https://api.pns.hk/api/v2/pnshk/categories/multi/{subcat_code}?lang=zh_HK&curr=HKD'
                yield scrapy.Request(url=url, callback=self.subcat, headers=self.payload, 
                    meta={'subcat_code': subcat_code, 'subcat_name': subcat_name, 'crawl_type': 'subcat'}, 
                    errback=self.handle_failure)
                
    def subcat(self, response):
        page_size = 1000

        subcat_code = response.meta['subcat_code']
        subcat_name = response.meta['subcat_name']
        cat_list = self.extract_response(response)

        if not isinstance(cat_list, list):
            cat_list = [cat_list]

        if len(cat_list) != 0:
            for subcat in cat_list:
                sub_subcat_code = subcat.get('code')
                sub_subcat_name = subcat.get('name')
                self.logger.info(f'sub cat code: {sub_subcat_code}, {sub_subcat_name}')
                with open(self.settings.get('SUBCAT_PATH'), 'a') as f:
                    f.write(f"{subcat_name},{subcat_code},{sub_subcat_name},{sub_subcat_code}\n")

    def handle_failure(self, failure):
        self.logger.error(f"This is a error on {failure.request.url}")
        failure_page = failure.request.meta.get('crawl_type')
        if failure_page == 'subcat':
            yield scrapy.Request(url=failure.request.url, callback=self.subcat, headers=self.payload, 
                    meta=failure.request.meta, errback=self.handle_failure)
