from ichrisbirch.wsgi import app


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6000, debug=True)