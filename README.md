# iperf3-prometheus

An iperf3 exporter and Docker stack for gathering iperf3 stats from long running tests and making the available via Prometheus. These stats can then be easily visualized with Grafana. The Prometheus stats are protected behind Nginx with Basic Auth and TLS. A bash script is included to run the tests from the client machines.

## Design

Because iperf3 only outputs JSON stats at the end of a test, the bash script runs iperf3 in batches of 1 minute runs. When a test run is complete, the Prometheus exporter reads the JSON stats and exposes them to Prometheus. These stats will continue to be updated at the end of each short iterative run. When the test script ends, the exporter will notice the lack of connection and zero the stats until a new run starts.

## Usage

### docker-compose

The docker-compose.yaml file is provided to deploy the exporter with iperf3, Prometheus, and the Nginx protection for the Prometheus endpoint. Its default is to expect Let's Encrypt certificates installed in the default location on the host system. This can be modified to use any certificates on the host or you can modify the Docker build to include them in the container.

### Building the Docker image

To build the docker image, simply start the docker-compose stack with `docker compose up -d`.

### Prometheus Stats

Prometheus stats are available from the standard Prometheus port (9090). This can be modified by changing the docker-compose.yaml file.

You must create the local `prometheus_data` storage directory on the host and this directory must be owned by `nobody:nogroup`. This is because the Prometheus container runs as the nobody user. You can adjust the location of this directory in the docker-compose.yaml file.

### Prometheus Basic Auth Protection

Prometheus is fronted with Nginx which provides TLS and Basic Auth protection. A username password combo needs to be set in the .htpasswd file. This file is created with the apache2 `htpasswd` utility.  See the `.htpassword` file for instructions on creating this file.

### iperf3-test.sh script

Usage information from this script is provided via the help (`--help`) option.
