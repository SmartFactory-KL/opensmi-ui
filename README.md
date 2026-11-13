# OpenSMI UI

This is the python based backend for OpenSMI

> [!important]
> This is not ready to use. Please wait until the release of v0.1.0 before starting to use it. Up until then, it is only considered an experimental UI.

## Quick Start

Run the docker container:

```bash
docker run -it -p 8000:8000 smartfactorykl/opensmi-ui:0.1.0-alpha.2
```

### With config.yaml

Create a `config.yaml` and copy the content of [Config YAML Example](docs/config/config.example.yaml) and set settings as you like.

Run the docker container:

```bash
docker run -it -v ./config.yaml:/app/config.yaml:ro -p 8000:8000 smartfactorykl/opensmi-ui:0.1.0-alpha.2
```

Open the Connect Page by clicking on the Logo and then `Establish Connection`. 
After you connected, remember to `Browse`. Use `Load Model` to reload from server.

As of now, the default is Port 8000.
