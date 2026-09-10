# OpenSMI UI

This is the python based backend for OpenSMI

# How to build locally

Please refer to [Building locally](docs/LocalBuild.md)

# How to run

## Virtual Environment

I use a virtual environment to develop this project using the [FastAPI Virtual Environments Tutorial](https://fastapi.tiangolo.com/virtual-environments/)
To create it, I used:

```bash
python -m venv .venv
```

Afterwards, to get a terminal within this virtual environment, I used:

```bash
source .venv/bin/activate
```

Which results in `(.venv)` being added to the front of my terminal line.

To leave it, use:

```bash
deactivate
```

## Install dependencies

First install the requirements for production use:

```bash
pip install -r requirements.txt
```

There are also some development-only requirements:

```bash
pip install -r requirements.dev.txt
```

## Run the dev server

After that, use the fastapi dev command to run a dev server with reloading and stuff:

```bash
fastapi dev
```

The API should now be available at `localhost:8000`.

Documentation is available at:

- [localhost:8000/docs](http://localhost:8000/docs) for Swagger

> [!note]
> The API is also described in [docs/openapi.yaml](docs/openapi.yaml). Use something like [https://editor-next.swagger.io/](https://editor-next.swagger.io/) to view it.

# Configuration

The available environment config options are documented in [DefaultConfiguration.md](docs/DefaultConfiguration.md)

### Locking and Pin Guard
Contrary to prior versions, starting with 25.06 the ModuleUI has two independant locking functionalities: 
Machine Locking and the Pin Guard.

The Machine Locking is controlled by the machines. It can either be enabled, disabled or simulated.

The Pin Guard is a instance-wide lock. When locked, all writes are blocked, including making changes to the current connection. 

### `config.yml` file

You can specify a `config.yml` file and add your configuration into it.
Key value pairs in this file will always take top priority and are simply overwriting existing configurations.

To use it while using the docker image, you will need to bind your file to `/app/config.yml` within the container (preferably as `:ro`)

> [!note]
> Be advised, that `config.yml` is part of the `.gitignore` on purpose, to prevent accidental config predefinitions from happening (again).

# Git hooks

To ensure that important docs are up-to-date, some [Git hooks are used](/docs/git-hooks/GitHooks.md)
