from livereload import Server, shell

from render_pages import render_pages

from livereload import Server, shell

server = Server()
server.watch('template.html', render_pages)
server.serve(root='.')