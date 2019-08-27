import scrapy


class SiteProductItem(scrapy.Item):
    product_name = scrapy.Field()
    product_details = scrapy.Field()
    specifications = scrapy.Field()

class MyScraper(scrapy.Spider):
    name = "scrapingdata"
    allowed_domains = ['www.apmex.com']
    DOMAIN_URL = 'https://www.apmex.com/'
    LOGIN_URL = 'https://www.apmex.com/account/login'
    START_URL = 'https://www.apmex.com/search?q=&x=9&y=16'
    USERNAME = 'marincess000@gmail.com'
    PASSWORD = 'prime12345'

    def __init__(self, **kwargs):

        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
                        'Content-Type': 'application/x-www-form-urlencoded',
                        }

    def start_requests(self):

        start_url = self.START_URL
        yield scrapy.Request(url=start_url, callback=self.parse_pagination)

    def parse_pagination(self, response):

        for page_num in range(1, 298):
            page_url = "https://www.apmex.com/search?page={}&x=9&y=16&ipp=120".format(page_num)
            yield scrapy.Request(url=page_url, callback=self.parse_pages,
                                 headers=self.headers, dont_filter=True)

    def parse_pages(self, response):

        detail_page_urls = response.xpath('//div[@class="product_item_image container"]/a/@href').extract()
        for detail_page_url in detail_page_urls:
            yield scrapy.Request(url=self.DOMAIN_URL + detail_page_url, callback=self.parse_product,
                                 headers=self.headers, dont_filter=True)

    def parse_product(self, response):

        prod_item = SiteProductItem()
        product_name = self._parse_product_name(response)
        prod_item['product_name'] = product_name
        product_details = self._parse_product_details(response)
        prod_item['product_details'] = product_details
        specifications = self._parse_specifications(response)
        prod_item['specifications'] = specifications

        yield prod_item

    @staticmethod
    def _parse_product_name(response):
        title = ""
        assert_title = response.xpath('.//h1[@class="product-title"]/text()').extract()
        if assert_title:
            title = str(assert_title[0].strip())
        return title

    @staticmethod
    def _parse_product_details(response):
        product_details = ""
        text_list = response.xpath('.//div[@class="tab-content details"]//text()').extract()
        for text in text_list:
            product_details += str(text.strip()) + " "
        result_product_details = product_details.replace("See More +", "")
        return result_product_details

    @staticmethod
    def _parse_specifications(response):
        specifications = ""
        li_list = response.xpath('.//ul[contains(@class, "product-table")]/li')
        for li_element in li_list:
            item = li_element.xpath('./text()').extract()[0]
            value = li_element.xpath('./span/text()').extract()[0]
            specification = item + value
            specifications += str(specification.strip()) + ",  "

        return specifications
