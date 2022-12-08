import logging
from bs4 import BeautifulSoup
import requests
import os
from pathvalidate import sanitize_filename
from urllib.parse import urlparse
import argparse

os.makedirs("books", exist_ok=True)
os.makedirs("img", exist_ok=True)
os.makedirs("comments", exist_ok=True)

def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError



def parse_book_page(html):

    soup = html
    title = soup.find('h1').text
    sanitize_filename(title)
    img = soup.find("div", class_="bookimage").find("img")["src"]
    img = f"https://tululu.org{img}"
    comments = soup.find("div", id="content").find_all("span", class_="black")
    comments_txt = ""
    genre = soup.find("span", class_="d_book").text
    genre = genre.split(" ")[3]
    for i in comments:
        comments_txt = comments_txt + f"{i.text}\n"

    try:
        title, author = title.split("::")
    except TypeError:
        title = "0"
        author = "0"


    book = {
        "title": title.strip(),
        "author": author.strip(),
        "genre": genre,
        "img": img
    }


    return book


def download_book(title, id, img_url, genre):
    payload ={
        "id": id
    }
    url = "https://tululu.org/txt.php"
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    img_response = requests.get(img_url)
    img_response.raise_for_status()
    check_for_redirect(img_response)
    with open(f"img/{id}.jpg", 'wb') as file:
        file.write(img_response.content)
    with open(f"books/{id}.{title} {genre}.txt", 'wb') as file:
        file.write(img_response.content)


def main():
    parser = argparse.ArgumentParser(
        description='Скачиват данные книги'
    )
    parser.add_argument('--start_num', help='С какой книги', default=1)
    parser.add_argument('--end_num', help='До какой книги', default=10)
    args = parser.parse_args()
    start_num = int(args.start_num)
    end_num = int(args.end_num)
    for id in range(start_num, end_num):
        try:
            url = f'https://tululu.org/b{id}/'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)

            html = BeautifulSoup(response.text, 'lxml')
            book = parse_book_page(html)
            download_book(book["title"], id, book["img"], book["genre"])
        except requests.exceptions.HTTPError:
            logging.warning("Было перенаправление")
            continue





if __name__=="__main__":
    main()
