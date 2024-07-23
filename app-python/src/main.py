from flask import Flask, Response
from prometheus_client import start_http_server, Gauge, generate_latest
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import requests

app = Flask(__name__)


def get_dockerhub_repositories():
    url = f'https://hub.docker.com/v2/repositories/{DOCKERHUB_ORGANIZATION}/'
    response = requests.get(url)
    response.raise_for_status()
    repositories = response.json()

    image_pulls = {}
    for image in repositories['results']:
        image_name = image['name']
        pull_count = image['pull_count']
        image_pulls[image_name] = pull_count

    return image_pulls

@app.route('/metrics')
def metrics():
    image_pulls = get_dockerhub_repositories()
    for image_name, pull_count in image_pulls.items():
        DOCKER_IMAGE_PULLS.labels(image=image_name,organization=DOCKERHUB_ORGANIZATION).set(pull_count)
    return Response(
            response= generate_latest(),
            content_type="text/plain"
        )

def server():
    port = int(os.environ.get('APP_PORT', 2113))
    debug= bool(os.environ.get('APP_DEBUG',True))
    
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    DOCKER_IMAGE_PULLS = Gauge('docker_image_pulls', 'Number of DockerHub image pulls', ['image','organization'])
    DOCKERHUB_ORGANIZATION = os.environ.get('DOCKERHUB_ORGANIZATION', "amazon")
    
    server()
