import json
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
import argparse


def render_pages():
    parser = argparse.ArgumentParser(
        description="Скачиват данные книги"
    )
    parser.add_argument("--json_path", help="путь хранения json файла", default="books_info.json")
    args = parser.parse_args()
    json_path = args.json_path
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )

    template = env.get_template("template.html")

    with open(json_path, "r") as file:
        books = json.load(file)
    books_quantity = 20
    books_info = list(chunked(books, books_quantity))
    for number, books_on_page in enumerate(books_info):
        rendered_page = template.render(
            books=books_on_page,
            pages=len(books_info),
            current_page=number,
        )
        with open(f"pages/index{number}.html", "w", encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == "__main__":
    render_pages()
