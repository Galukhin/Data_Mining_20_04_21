import time
import typing
import datetime
import requests
from urllib.parse import urljoin
from pymongo import MongoClient
import bs4


"""
Источник https://gb.ru/posts/
Необходимо обойти все записи в блоге и извлечь из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
Структуру сохраняем в MongoDB
"""


class GbBlogParse:
    def __init__(self, start_url, collection):
        self.time = time.time()
        self.start_url = start_url
        self.collection = collection
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)

    def _get_response(self, url, *args, **kwargs):
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        print(url)
        return response

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in tags_list
            if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def get_comments(self, url):
        response = self._get_response(url)
        data = response.json()
        return data

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_post(self, url, soup):
        title_tag = soup.find("h1", attrs={"class": "blogpost-title"})

        first_img = soup.find("div", attrs={"class": "blogpost-content"}).find("img")
        if first_img: # Попались статьи без картинок
            first_img_link = first_img.attrs.get("src")
        else:
            first_img_link = None

        date_published = soup.find("div", attrs={"class": "blogpost-date-views"}).find("time").attrs.get("datetime")
        date_obj = datetime.datetime.strptime(date_published, '%Y-%m-%dT%H:%M:%S%z')

        author_name = soup.find("div", attrs={"itemprop": "author"}).text
        author_link = urljoin("https://gb.ru", soup.find("div", attrs={"itemprop": "author"}).parent["href"])

        commentable_id = soup.find("comments")["commentable-id"]
        comments = self.get_comments(f'https://gb.ru/api/v2/comments?commentable_type=Post&'
                                     f'commentable_id={commentable_id}&order=desc')
        data = {
            "url": url,
            "title": title_tag.text,
            "first_img": first_img_link,
            "date_published": date_obj,
            "author_name": author_name,
            "author_link": author_link,
            "comments": comments
        }
        return data

    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    def save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    collection = MongoClient()["gb_parse_20_04"]["gb_blog"]
    parser = GbBlogParse("https://gb.ru/posts", collection)
    parser.run()
