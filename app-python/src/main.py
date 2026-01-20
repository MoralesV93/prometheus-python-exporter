from datetime import datetime, timezone
import os
from prometheus_client import Gauge, generate_latest
from flask import Flask, Response,jsonify
from dateutil import parser
import requests


app = Flask(__name__)


def get_image_list_by_time_frame(image_list:list):
    now = datetime.now(timezone.utc)
    image_sorted = sorted(image_list, key=lambda imagerror:image['last_updated'],reverse=True)
    image_list = []
    for image in image_sorted:
        last_updated = parser.isoparse(image['last_updated'])
        if (now - last_updated).total_seconds()<=IMAGE_TIME_FRAME_SECONDS:
            image_list.append(image)
        else:
            break
    return image_list


def get_dockerhub_repositories():
    try:
        url = f'{DOCKERHUB_REGISTRY_URL}/{DOCKERHUB_ORGANIZATION}/'
        response = requests.get(url)
        response.raise_for_status()
        repositories = response.json()
        images_list = get_image_list_by_time_frame(repositories['results'])
        image_pulls = {}
        for image in images_list:
            image_name = image['name']
            pull_count = image['pull_count']
            image_pulls[image_name] = pull_count

        return image_pulls
    except Exception as error:
        raise error

@app.route('/metrics')
def metrics():
    try:
        image_pulls = get_dockerhub_repositories()
        for image_name, pull_count in image_pulls.items():
            DOCKER_IMAGE_PULLS.labels(image=image_name,organization=DOCKERHUB_ORGANIZATION).set(pull_count)
        return Response(
                response= generate_latest(),
                content_type="text/plain"
            )
    except requests.exceptions.HTTPError as http_err:
        return Response(
            response=jsonify({'error': f'HTTP error occurred: {http_err}'}),
            content_type="application/json",
            status=500
            )
    except requests.exceptions.ConnectionError as http_err:
        return Response(
            response=jsonify({'error': f'ConnectionError error occurred: {http_err}'}),
            content_type="application/json",
            status=500
            )
    except Exception as error:
        return Response(
            response={"error":str(error)},
            content_type="application/json",
            status=500
        )

def server():
    port = int(os.environ.get('APP_PORT', 2113))
    debug= bool(os.environ.get('APP_DEBUG',True))
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    DOCKER_IMAGE_PULLS = Gauge('docker_image_pulls', 'Number of DockerHub image pulls', ['image','organization'])
    IMAGE_TIME_FRAME_SECONDS = int(os.environ.get('IMAGE_TIME_FRAME_SECONDS', 5))
    DOCKERHUB_REGISTRY_URL = os.environ.get('DOCKERHUB_REGISTRY_URL','https://hub.docker.com/v2/repositories')
    DOCKERHUB_ORGANIZATION = os.environ.get('DOCKERHUB_ORGANIZATION', "amazon")
    server()
