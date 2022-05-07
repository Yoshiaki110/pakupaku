# -*- coding: utf-8 -*-

# https://tech-blog.cloud-config.jp/2021-12-11-make-flask-app-on-azure-app-service/

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
  app.run(debug=True)

