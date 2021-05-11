# from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose
from urllib.parse import urljoin


def get_url(itm):
    return urljoin("https://www.avito.ru", itm)


def get_price(itm):
    itm = itm.replace(" ", "")
    return float(itm)


def get_addr(itm):
    itm = itm.replace("\n ", "")
    return itm


def get_params(data):
    data = [itm.replace(": ", "") for itm in data if (itm != ' ') and (itm != '\n  ')]
    data = [itm[:-1] if itm[-1] == ' ' else itm for itm in data]
    result = {}
    for idx in range(int(len(data) / 2)):
        result.update({data[idx * 2]: data[idx * 2 + 1]})
    return result


class FlatLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    seller_url_in = MapCompose(get_url)
    seller_url_out = TakeFirst()
    price_in = MapCompose(get_price)
    price_out = TakeFirst()
    address_in = MapCompose(get_addr)
    address_out = TakeFirst()
    parameters_out = Compose(get_params)
