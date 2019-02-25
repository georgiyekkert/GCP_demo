from google.cloud import pubsub
from flask import current_app
from .models import get, update, Memes

from google.cloud import vision
import psq

publisher_client = pubsub.PublisherClient()
subscriber_client = pubsub.SubscriberClient()
vision_client = vision.ImageAnnotatorClient()


def create_queue(name):
    project = current_app.config['PROJECT_ID']

    return psq.Queue(
        publisher_client, subscriber_client, project,
        name, extra_context=current_app.app_context)


def annotate(id):
    url = get(id, Memes)['url']
    type = get_img_annotation(url)
    data = {'labels': type}
    update(data, id, Memes)


def get_img_annotation(file_location):
    response = vision_client.annotate_image(({
        'image': {'source': {'image_uri': file_location}},
        'features': [{'type': vision.enums.Feature.Type.LABEL_DETECTION}],
    }))
    return response.label_annotations[0].description
