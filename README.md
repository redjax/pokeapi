# PokeAPI

![PokeAPI logo](https://raw.githubusercontent.com/PokeAPI/media/master/logo/pokeapi_256.png "PokeAPI")

*Disclaimer: This project is not associated with the PokeAPI site in any way.*

Utilities & example apps to interact with the [Pokemon API](pokeapi.co/).

## Requirements

- [Docker](https://www.docker.com)
- [PDM](https://pdm-project.org/latest/)

## Setup

This app is configured with [`Dynaconf`](https://www.dynaconf.com). When running in Docker, make sure to rename the file `settings.toml` file in the [PokeAPI app's `config/` directory](./apps/pokeapi/src/config/) to `settings.toml.bak` so that env variables can be loaded from the Docker environment.

### Docker

* Copy `.env` -> `.env`
  * Optionally, set variables like `ENV=dev` and `LOG_LEVEL=DEBUG` to change the functionality of the project.
* Run `docker compose build` to build the project containers
* Run `docker compose up -d` to start the apps

### Local (PDM venv)

When running locally, environment variables are loaded from TOML files in [the app's `config/` dir](`./apps/pokeapi/src/config/`).

**DO NOT DIRECTLY MODIFY `settings.toml`**

Instead, copy `./apps/pokeapi/src/config/settings.toml` -> `./apps/pokeapi/src/config/settings.local.toml`. Edit the variables in the new `settings.local.toml` file to change the behavior of the app.

## Usage

The project source has multiple entrypoints, which can be run locally with the project's virtual environment, or in a Docker Compose stack.

Running the Docker stack with `docker compose up -d` spawns multiple containers networked together to enable requests between them.

Containers:

- Refresh caches
  - Builds the container with the script to refresh all caches.
  - Uses the Celery worker container to execute long-running refresh commands.
  - Make requests to get all Pokemon resources from the API (includes Pokemon name & the URL to request data for that Pokemon), then loops over each resource and requests the Pokemon's data.
    - As requests are made, the responses are cached to the disk for 24 hours.
- Celery worker
  - Builds the container with the Celery worker start command. The worker makes a connection to the RabbitMQ container to run background tasks using the queue, and connects to Redis for the Celery task backend.
- RabbitMQ
  - Message queue for the Celery worker
- Redis
  - Task backend for Celery
- Prometheus
  - Collect logs from RabbitMQ container
- Grafana
  - Connect to the Prometheus container & graph stats/logs from RabbitMQ
