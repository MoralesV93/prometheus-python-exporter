# Prometheus Python Exporter

A Prometheus exporter built with Python and Flask that monitors DockerHub image pull statistics for a specified organization. This exporter fetches pull count metrics from the DockerHub API and exposes them in Prometheus format.

## Overview

This project provides a containerized Prometheus exporter that:
- Monitors DockerHub repositories for a specified organization
- Tracks the number of image pulls for each repository
- Filters images based on a configurable time frame
- Exposes metrics in Prometheus-compatible format
- Can be easily deployed on Kubernetes using Helm charts

## Architecture

### Project Structure

```
prometheus-python-exporter/
├── app-python/                 # Python application source
│   ├── Dockerfile             # Docker container image definition
│   ├── requirements.txt        # Python dependencies
│   └── src/
│       ├── __init__.py
│       └── main.py            # Main application code
├── k8s-resources/             # Kubernetes deployment resources
│   ├── app.yml               # Kubernetes app deployment manifest
│   ├── utils.yml             # Kubernetes utility resources
│   └── Charts/
│       └── exporter/         # Helm chart for the exporter
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│               ├── _helpers.tpl
│               ├── app-configmap.yaml
│               ├── app-service.yaml
│               └── app.yaml
└── README.md                  # This file
```

## Features

- **DockerHub Integration**: Automatically pulls image statistics from DockerHub API
- **Time-Based Filtering**: Only includes images updated within a specified time frame
- **Prometheus Metrics**: Exposes `docker_image_pulls` gauge metric with image and organization labels
- **Configurable**: Supports multiple environment variables for customization
- **Docker Support**: Containerized for easy deployment
- **Kubernetes Ready**: Includes Helm chart for Kubernetes deployment
- **Prometheus Integration**: Includes Helm-based Prometheus monitoring

## Dependencies

- **Flask**: 3.0.3 - Web framework for HTTP server
- **prometheus_client**: 0.20.0 - Prometheus metrics client library
- **python-dateutil**: 2.9.0 - Date/time parsing utilities
- **requests**: 2.32.3 - HTTP client library
- **urllib3**: 2.2.2 - HTTP client library

## Configuration

### Environment Variables

The application supports the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PORT` | `2113` | Port on which the Flask server listens |
| `APP_DEBUG` | `true` | Enable Flask debug mode |
| `DOCKERHUB_ORGANIZATION` | `amazon` | DockerHub organization name to monitor |
| `DOCKERHUB_REGISTRY_URL` | `https://hub.docker.com/v2/repositories` | DockerHub API base URL |
| `IMAGE_TIME_FRAME_SECONDS` | `5` | Time frame in seconds to filter recent images |

## Metrics

### Exposed Metrics

- **`docker_image_pulls`** (Gauge): Number of DockerHub image pulls
  - Labels:
    - `image`: The name of the Docker image
    - `organization`: The organization name

Example:
```
docker_image_pulls{image="ubuntu",organization="amazon"} 1000000
docker_image_pulls{image="aws-cli",organization="amazon"} 500000
```

## Building

### Build Docker Image

```bash
cd app-python
docker build -t prometheus-python-exporter:1.0.0 .
```

### Running Locally

#### Prerequisites
- Python 3.9+
- pip

#### Installation

```bash
cd app-python
pip install -r requirements.txt
```

#### Running the Application

```bash
cd app-python/src
python main.py
```

The exporter will start on `http://localhost:2113`

#### Accessing Metrics

```bash
curl http://localhost:2113/metrics
```

## Deployment

### Docker Deployment

```bash
docker run -d \
  -p 2113:2113 \
  -e DOCKERHUB_ORGANIZATION=amazon \
  -e IMAGE_TIME_FRAME_SECONDS=13114080 \
  --name prometheus-exporter \
  prometheus-python-exporter:1.0.0
```

### Kubernetes Deployment with Helm

#### Prerequisites
- Kubernetes cluster
- Helm 3.x installed

#### Install the Chart

```bash
helm dependency update k8s-resources/Charts/exporter
helm install prometheus-exporter k8s-resources/Charts/exporter
```

#### Customize Configuration

Create a custom `values.yaml`:

```yaml
image:
  repository: your-registry/p-exporter-app
  tag: 1.0.0

env:
  DOCKERHUB_ORGANIZATION: your-organization
  IMAGE_TIME_FRAME_SECONDS: "13114080"
```

Install with custom values:

```bash
helm install prometheus-exporter k8s-resources/Charts/exporter -f custom-values.yaml
```

#### Verify Deployment

```bash
kubectl get pods -l app=p-exporter-app
kubectl port-forward svc/p-exporter-app 2113:2113
curl http://localhost:2113/metrics
```

## API Endpoints

- **`/metrics`**: Prometheus metrics endpoint (GET)
  - Returns metrics in Prometheus text format
  - Content-Type: `text/plain`
  - Fetches latest DockerHub image data on each request

## Error Handling

The application handles the following error scenarios:

- **HTTP Errors**: Returns 500 status with error message if DockerHub API request fails
- **Connection Errors**: Returns 500 status with error message if unable to connect to DockerHub API
- **General Exceptions**: Returns 500 status with error details for any unexpected errors

## Helm Chart Details

The included Helm chart deploys:
- The Python exporter application as a Kubernetes Deployment
- A Service (NodePort type) exposing port 2113
- ConfigMaps for configuration
- Prometheus Helm chart with custom scrape configuration
- Prometheus scrapes the exporter every 1 minute with a 30-second timeout

### Chart Values

Key configuration options in `values.yaml`:
- `image.repository`: Container registry URL
- `image.tag`: Container image tag
- `service.type`: Kubernetes service type
- `env.*`: Environment variables for the application
- `prometheus.*`: Prometheus Helm chart configuration

## Monitoring

The exporter is configured to be scraped by Prometheus with the following settings:
- **Job Name**: `python-exporter`
- **Scrape Interval**: 1 minute
- **Scrape Timeout**: 30 seconds
- **Target**: `p-exporter-app:2113`

## Development

### Code Structure

- **main.py**: Contains the Flask application and Prometheus exporter logic
  - `get_dockerhub_repositories()`: Fetches image data from DockerHub API
  - `get_image_list_by_time_frame()`: Filters images by time frame
  - `metrics()`: Flask route that handles `/metrics` requests and generates Prometheus output
  - `server()`: Starts the Flask development server

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions, please [add support contact information].
