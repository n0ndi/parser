import logging
from bs4 import BeautifulSoup
import requests
import os
from pathvalidate import sanitize_filename
from urllib.parse import urlparse, urljoin
import argparse
from time import sleep


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError



def parse_book_page(page_content):

    soup = page_content
    title = soup.find('h1').text
    #sanitize_filename(title)
    img_url = soup.find("div", class_="bookimage").find("img")["src"]
    img_url = urljoin("https://tululu.org",img_url)
    comments = soup.find("div", id="content").find_all("span", class_="black")
    comments_txt = [comment.text for comment in comments]
    genre = soup.find("span", class_="d_book").text
    genre = sanitize_filename(genre)


    title, author = title.split("::")


    book = {
        "title": title.strip(),
        "author": author.strip(),
        "genre": genre,
        "img_url": img_url
    }


    return book


def download_book_img(title, id, img_url):
    img_response = requests.get(img_url)
    img_response.raise_for_status()
    check_for_redirect(img_response)
    with open(f"img/{id}.{title}.jpg", 'wb') as file:
        file.write(img_response.content)


def download_text_book(title, id, genre):
    payload ={
        "id": id
    }
    url = "https://tululu.org/txt.php"
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    with open(f"books/{id}.{title} {genre}.txt", 'wb') as file:
        file.write(response.content)



def main():
    parser = argparse.ArgumentParser(
        description='Скачиват данные книги'
    )
    parser.add_argument('--start_num', type=int, help='С какой книги', default=1)
    parser.add_argument('--end_num', type=int, help='До какой книги', default=10)
    args = parser.parse_args()
    start_book = args.start_num
    end_book = args.end_num
    for id in range(start_book, end_book):
        while True:
            try:
                url = f'https://tululu.org/b{id}/'
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)

                page_content = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(page_content)
                download_text_book(book["title"], id, book["genre"])
                download_book_img(book["title"], id, book["img_url"])
                break
            except requests.exceptions.HTTPError:
                logging.warning("Было перенаправление")
                break
            except requests.exceptions.ConnectionError:
                logging.warning("Ошибка соединения")
                sleep(5)



if __name__=="__main__":
    os.makedirs("books", exist_ok=True)
    os.makedirs("img", exist_ok=True)
    os.makedirs("comments", exist_ok=True)
    main()
