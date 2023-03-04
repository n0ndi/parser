import logging
from bs4 import BeautifulSoup
import requests
import os
from pathvalidate import sanitize_filename
from urllib.parse import urlparse, urljoin
import argparse
from time import sleep
import json




def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError



def parse_book_page(page_content, id):
    soup = page_content
    title = soup.select_one("h1").text
    img_url = soup.select_one("div.bookimage img")["src"]
    img_url = urljoin(f"https://tululu.org/b{id}", img_url)
    comments = soup.select("div.content span.black")
    comments_txt = [comment.text for comment in comments]
    genres = soup.select("span.d_book a")
    genres = [ genre.text for genre in genres]


    title, author = title.split("::")


    book = {
        "title": title.strip(),
        "author": author.strip(),
        "genres": genres,
        "img_url": img_url
    }


    return book


def download_book_img(dest_folder, title, id, img_url):
    img_response = requests.get(img_url)
    img_response.raise_for_status()
    check_for_redirect(img_response)
    dir_path = os.path.join(dest_folder, "img")
    file_name = sanitize_filename(f"{id}.{title}.jpg")
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'wb') as file:
        file.write(img_response.content)
    return file_path

def download_text_book(dest_folder, title, id, genres):
    payload ={
        "id": id
    }
    url = "https://tululu.org/txt.php"
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    dir_path = os.path.join(dest_folder, "books")
    file_name = sanitize_filename(f"{id}.{title} {genres}.txt")
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def main():
    os.makedirs("books", exist_ok=True)
    os.makedirs("img", exist_ok=True)
    os.makedirs("comments", exist_ok=True)
    parser = argparse.ArgumentParser(
        description='Скачиват данные книги'
    )
    parser.add_argument('--start_num', type=int, help='С какой книги', default=1)
    parser.add_argument('--end_num', type=int, help='До какой книги', default=10)
    args = parser.parse_args()
    start_book = args.start_num
    end_book = args.end_num
    for book_id in range(start_book, end_book):
        while True:
            try:
                url = f'https://tululu.org/b{book_id}/'
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)

                page_content = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(page_content, book_id)
                download_text_book(book["title"], book_id, book["genres"])
                download_book_img(book["title"], book_id, book["img_url"])
                break
            except requests.exceptions.HTTPError:
                logging.warning("Было перенаправление")
                break
            except requests.exceptions.ConnectionError:
                logging.warning("Ошибка соединения")
                sleep(5)



if __name__=="__main__":
    main()
