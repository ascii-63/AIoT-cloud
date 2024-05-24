from flask import Flask, jsonify, send_file
import pika
import json
import requests
from io import BytesIO
from PIL import Image
import threading

app = Flask(__name__)
messages = []
amqp_url = "amqp://admin:admin@localhost:5672/"
queue_name = "message"


def callback(ch, method, properties, body):
    global messages
    message = json.loads(body)
    messages.append(message)
    if len(messages) > 1:
        messages.pop(0)


def consume_queue():
    connection_parameters = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


@app.route('/logs', methods=['GET'])
def get_logs():
    global messages
    return jsonify(messages)


@app.route('/image', methods=['GET'])
def get_image():
    if messages:
        image_url = messages[0].get('url')
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=70)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    return jsonify({'error': 'No image available'}), 404


if __name__ == '__main__':
    threading.Thread(target=consume_queue).start()
    app.run(debug=True)
