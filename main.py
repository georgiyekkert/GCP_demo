import overviewer

app = overviewer.create_app()

with app.app_context():
    queue = overviewer.queue_tasks.create_queue(name="image")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8085, debug=True)
