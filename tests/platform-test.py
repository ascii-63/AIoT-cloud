import pika
import os
import sys
import json
import requests
from datetime import datetime


ENV_FILE = '.env'
TEMP_DIR = '.temp'

############################################


def getTimestampFromMessage(msg: str) -> str:
    '''Get timestamp go with this message `msg`'''

    data = json.loads(msg)
    timestamp_str = data.get('@timestamp')
    if timestamp_str:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return timestamp
    else:
        return None


def getImageURLFromMessage(msg: str) -> str:
    '''Get image URL go with this message `msg`'''

    data = json.loads(msg)
    try:
        image_url = data.get('image_URL')
        return image_url
    except Exception as e:
        print(f'[ERROR] Exeption: {e}')
        return None


def getVideoURLFromMessage(msg: str) -> str:
    '''Get video URL go with this message `msg`'''

    data = json.loads(msg)
    try:
        image_url = data.get('video_URL')
        return image_url
    except Exception as e:
        print(f'[ERROR] Exeption: {e}')
        return None


def getFileNameFromURL(url: str) -> str:
    '''Get file name (image or video) from a URL'''

    def get_substr(s: str, keyword: str) -> str:
        pos = s.find(keyword)
        if pos != -1:
            return s[pos:]
        return ''

    image = get_substr(url, 'images')
    video = get_substr(url, 'videos')
    if image != '':
        return image
    elif video != '':
        return video
    return None


def downloadContent(url: str):
    """
    Downloads an content from a given URL.
    """

    try:
        response = requests.get(url)

        if response.status_code == 200:
            file_name = getFileNameFromURL(url)
            with open(file_name, 'wb') as file:
                file.write(response.content)

        else:
            print(
                f'Failed to retrieve the content. Status code: {response.status_code}')
    except Exception as e:
        print(f'[ERROR] An error occurred: {e}')

############################################


# Read and parse the .env file
with open(ENV_FILE) as f:
    for line in f:
        if line.strip() and not line.strip().startswith("#"):
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

amqp_url = os.environ.get('AMQP_URL')
queue_name = os.environ.get('QUEUE')

############################################

connection_parameters = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()
channel.queue_declare(queue=queue_name, durable=True)


def callback(ch, method, properties, body):
    '''Callback function to process incoming messages'''

    decoded_message = body.decode('utf-8')
    decoded_message = decoded_message.replace("\n", "")
    decoded_message = json.dumps(json.loads(decoded_message), indent='\t')
    print(f"\n{decoded_message}")

    image_url = getImageURLFromMessage(decoded_message)
    video_url = getVideoURLFromMessage(decoded_message)
    # print(f">_ Image URL: {image_url}")
    # print(f">_ Video URL: {video_url}")

    if image_url is not None:
        downloadContent(image_url)
    if video_url is not None:
        downloadContent(video_url)

    # ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback)

############################################

if __name__ == "__main__":
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
