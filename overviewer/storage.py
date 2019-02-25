import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
from flask import current_app
from google.cloud import storage
import six


def get_storage_client():
    return storage.Client(
        project=current_app.config['PROJECT_ID'])


def unique_name(filename):
    basename, extension = secure_filename(filename).rsplit('.', 1)
    return "{0}-{1}.{2}".format(basename, datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S"), extension)


def upload_file(file_stream, filename, content_type):
    if filename.split('.').pop().lower() not in ['jpg', 'img', 'png', 'jpeg']:
        raise BadRequest("Bad extension")

    bucket = get_storage_client().bucket(current_app.config['CLOUD_STORAGE_BUCKET'])
    blob = bucket.blob(unique_name(filename))

    blob.upload_from_string(
        file_stream,
        content_type=content_type)

    url = blob.public_url

    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    return url
