import os
import xmltodict, json
import csv

import scrapy

class PnshkProdSpider(scrapy.Spider):
    name = "pnshk_prod"
    payload={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/json,image/avif,image/webp,image/apng'
    }

    def start_requests(self):

        page_size = 1000
        with open(self.settings.get('SUBCAT_PATH'), 'r') as f:
            rows = csv.reader(f)
            for row in rows:
                subcat = row[-1]
                self.logger.info(f'start subcat: {subcat}')
                url = f'https://api.pns.hk/api/v2/pnshk/products/search?fields=FULL&query=%3AbestSeller%3Acategory%3A{subcat}&pageSize={page_size}&sort=bestSeller&lang=zh_HK&curr=HKD'
                yield scrapy.Request(url=url, callback=self.product_list, headers=self.payload, 
                    meta={'page': 1, 'page_size': page_size, 'crawl_type': 'product_list', 'subcat': subcat}, 
                            errback=self.handle_failure)

    def product_list(self, response):
        subcat = response.meta['subcat']
        page_size = response.meta['page_size']
        page = response.meta['page']
        try:
            self.logger.info(f'json')
            content = json.loads(response.body)
            products = content.get('products')
        except:
            try:
                self.logger.info(f'xmltodict')
                content = xmltodict.parse(response.body)
                products = content.get('productCategorySearchPage').get('products')
                self.logger.info(f'products {products}')
            except:
                self.logger.error(f'Error on product_list, retrying')
                yield scrapy.http.Request(response.url, callback=self.product_list, 
                        dont_filter=True, meta=response.meta)

        # self.logger.info(f'product: {content}')        
        if not isinstance(products, list):
            products = [products]

        for idx, i in enumerate(products):
            product_url = i.get('url')
            product_code = i.get('code')
            self.logger.info(f'current product code: {product_code}')
            url = f'https://www.pns.hk/zh-hk/p/{product_code}'
            yield scrapy.Request(url=url, callback=self.product_page, headers=self.payload, 
                meta={'product_code': product_code, 'crawl_type': 'product_page', 'subcat': subcat}, 
                            errback=self.handle_failure)

        if len(products) == page_size:
            page += 1
            url = f'https://api.pns.hk/api/v2/pnshk/products/search?fields=FULL&query=%3AbestSeller%3Acategory%3A{subcat}&pageSize={page_size}&currentPage={page}&sort=bestSeller&lang=zh_HK&curr=HKD' 
            yield scrapy.Request(url=url, callback=self.product_list, headers=self.payload, 
                meta={'page': 1, 'page_size': page_size, 'crawl_type': 'product_list', 'subcat': subcat}, 
                            errback=self.handle_failure)
        
    def product_page(self, response):
        subcat = response.meta['subcat']
        product_code = response.meta['product_code']
        css='pns-product-images .product-gallery .largePhoto e2-media img::attr(src)'
        css_info = 'script.structured-data::text'
        pic_list = response.css(css).get()
        product_info = response.css(css_info).get()
        self.logger.info(f'parsing product code page: {product_code}')

        if not isinstance(pic_list, list):
            pic_list = [pic_list]

        try:
            product_info = json.loads(product_info)
            product_name = product_info[1].get('name')
            product_brand = product_info[1].get('brand').get('name')

        except TypeError:
            self.logger.error(f'Error on {response.url}')
            self.logger.error(f'{response.body}')
            yield scrapy.http.Request(response.url, callback=self.product_page, dont_filter=True, meta=response.meta)

        else:
            with open(self.settings.get('PROD_INFO_PATH'), 'a') as f:
                f.write(f"{subcat},{product_code},{product_brand},{product_name}\n")

            for idx, i in enumerate(pic_list):
                image_type = i.split('?')[0].split('.')[-1]
                yield scrapy.Request(url=i, callback=self.image, headers=self.payload, 
                    meta={'product_code': product_code, 'index': idx, 'image_type': image_type, 
                    'crawl_type': 'image'},
                    errback=self.handle_failure)
            
    def image(self, response):
        product_code = response.meta['product_code']
        idx = response.meta['index']
        image_type = response.meta['image_type']
        base_path = self.settings.get('IMAGE_BASE_PATH')
        product_folder = base_path + '/' + product_code

        self.logger.info(f'image: {response.url}')
        if not os.path.exists(product_folder):
            os.makedirs(product_folder)
        
        img_path = f'{product_folder}/{idx}.{image_type}'
        if not os.path.exists(img_path):
            self.logger.info(f'new product image: {product_code}')
            with open(img_path, 'wb') as f:
                f.write(response.body)
                self.logger.info(f'save image as: {img_path}')

    def handle_failure(self, failure):
        self.logger.error(f"This is a error on {failure.request.url}")
        failure_page = failure.request.meta.get('crawl_type')
        if failure_page == 'product_list': 
            yield scrapy.Request(url=failure.request.url, callback=self.product_list, headers=self.payload,  
                    meta=failure.request.meta, errback=self.handle_failure)
        elif failure_page == 'product_page':
            yield scrapy.Request(url=failure.request.url, callback=self.product_page, headers=self.payload,  
                    meta=failure.request.meta, errback=self.handle_failure)
        elif failure_page == 'image':
            yield scrapy.Request(url=failure.request.url, callback=self.image, headers=self.payload,  
                    meta=failure.request.meta, errback=self.handle_failure)
