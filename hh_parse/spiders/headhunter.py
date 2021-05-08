import scrapy
from ..loaders import VacancyLoader, CompanyLoader
from ..items import VacancyItem, CompanyItem


class HeadhunterSpider(scrapy.Spider):
    name = 'headhunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _xpath_selectors = {
        "vacancy_pagination": "//div[@data-qa='pager-block']//a[@data-qa='pager-page']/@href",
        "vacancy_url": "//div[@class='vacancy-serp']//a[@data-qa='vacancy-serp__vacancy-title']/@href",
        "company_url": "//div[@data-qa='vacancy-company']//a[@data-qa='vacancy-company-name']/@href",
        "company_vacancies": '//div[@class="employer-sidebar-block"]'
                             '/a[@data-qa="employer-page__employer-vacancies-link"]/@href',
    }

    _xpath_data_vacancy_selectors = {
        "title": '//div[@class="vacancy-title"]/h1[@data-qa="vacancy-title"]/text()',
        "salary": '//div[@class="vacancy-title"]//p[@class="vacancy-salary"]/span/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="vacancy-section"]//div[@data-qa="bloko-tag bloko-tag_inline skills-element"]//text()',
        "company_url": "//div[@data-qa='vacancy-company']//a[@data-qa='vacancy-company-name']/@href",
    }

    _xpath_data_company_selectors = {
        "title": '//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()',
        "site": '//div[@class="employer-sidebar-content"]/a[@data-qa="sidebar-company-site"]/@href',
        "area_of_activity": '//div[@class="employer-sidebar-block"]/p/text()',
        "description": '//div[@data-qa="company-description-text"]/div[@class="g-user-content"]//text()',
    }

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._xpath_selectors["vacancy_pagination"], self.parse
        )
        yield from self._get_follow(
            response, self._xpath_selectors["vacancy_url"], self.vacancy_parse
        )

    def vacancy_parse(self, response):
        item = VacancyItem()
        vacancy_loader = VacancyLoader(response=response, item=item)
        vacancy_loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_vacancy_selectors.items():
            vacancy_loader.add_xpath(key, xpath)
        yield from self._get_follow(
            response, self._xpath_selectors["company_url"], self.company_parse
        )
        yield vacancy_loader.load_item()

    def company_parse(self, response):
        item = CompanyItem()
        company_loader = CompanyLoader(response=response, item=item)
        company_loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_company_selectors.items():
            company_loader.add_xpath(key, xpath)
        yield from self._get_follow(
            response, self._xpath_selectors["company_vacancies"], self.parse
        )
        yield company_loader.load_item()
