import json
from more_itertools import chunked
from pprint import pprint

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_pages():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open("books_info.json", "r") as file:
        books = json.load(file)



    books = chunked(books, 2)
    pages = list(chunked(books, 10))

    for number, page in enumerate(pages):
        rendered_page = template.render(
            books=page,
            pages=len(pages),
            current_page=number,
        )

        with open(f'pages/index{number}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

if __name__=="__main__":
    render_pages()