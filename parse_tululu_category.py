from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
from main import parse_book_page, download_book_img, download_text_book, check_for_redirect
import logging
import argparse
import json
import os
import time


def parse_book_category(start_page, end_page):
    books_urls = []
    for page in range(start_page, end_page):
        while True:
            try:
                url = f"https://tululu.org/l55/{page}/"
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)
                break
            except requests.exceptions.HTTPError:
                logging.warning("Было перенаправление")
                break
            except requests.exceptions.ConnectionError:
                logging.warning("Ошибка соединения")
                time.sleep(5)

        page_content = BeautifulSoup(response.text, "lxml")
        soup = page_content
        books = soup.select("div.bookimage a")
        for book in books:
            number_book = book["href"]
            books_urls.append(urljoin("https://tululu.org", number_book))
    return books_urls


def main():
    parser = argparse.ArgumentParser(
        description='Скачиват данные книги'
    )
    parser.add_argument("--start_page", type=int, help="С какой страницы", default=1)
    parser.add_argument("--end_page", type=int, help="До какой страницы", default=10)
    parser.add_argument("--dest_folder", type=str, help="Путь до каталого", default="")
    parser.add_argument("--skip_imgs", help="не скачивать картинки", action="store_true")
    parser.add_argument("--skip_txt", help="не скачивать текст", action="store_true")
    parser.add_argument("--json_path", help="путь скачки json файла", default="")
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path
    all_books_info = []
    os.makedirs(os.path.join(dest_folder, "media/books"), exist_ok=True)
    os.makedirs(os.path.join(dest_folder, "media/img"), exist_ok=True)
    for book_url in parse_book_category(start_page, end_page):
        while True:
            img_path = ""
            txt_path = ""
            try:
                response = requests.get(book_url)
                response.raise_for_status()
                check_for_redirect(response)
                page_content = BeautifulSoup(response.text, 'lxml')
                soup = page_content
                book_id = urlparse(book_url).path.replace("b", "").replace("/", "")
                book = parse_book_page(soup, book_id)
                if not skip_txt:
                    txt_path = download_text_book(os.path.join(dest_folder, "media"), book["title"], book_id, book["genres"])
                if not skip_imgs:
                    img_path = download_book_img(os.path.join(dest_folder, "media"), book["title"], book_id, book["img_url"])
                book_params = {
                    "id": book_id,
                    "title": book["title"],
                    "author": book["author"],
                    "genres":  book["genres"],
                    "img_path": img_path.replace("\\", "/"),
                    "txt_path": txt_path.replace("\\", "/")
                }
                all_books_info.append(book_params)
                break
            except requests.exceptions.HTTPError:
                logging.warning("Было перенаправление")
                break
            except requests.exceptions.ConnectionError:
                logging.warning("Ошибка соединения")
                time.sleep(5)
    json_path = os.path.join(json_path, "books_info.json")
    with open(json_path, "w") as file:
        json.dump(all_books_info, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
