from livereload import Server

from render_pages import render_pages


def main():
    render_pages()
    server = Server()
    server.watch('template.html', render_pages)
    server.serve(root='.')


if __name__ == "__main__":
    main()
