# Build locally

To create the docker container locally, the following steps need to be done: 

1. Clone and build the frontend
2. Copy the frontend dist files to the backend public folder
3. build the backend docker image

### Clone and build the frontend

> [!note]
> You need to have [NodeJS 22](https://nodejs.org/en/download) installed

~~~bash
git clone https://gitlab+deploy-token-158:gldt-rcirz95SsXUDEQTkpDXS@ifs.dfki.de/software-hub/opc-ua/vue-module-ui/module-ui-frontend.git
~~~

Remember to switch to the correct branch. Branches of backend and frontend need to match, for example:

~~~bash
git switch 25.06.0-dev
~~~

Once cloned, simply install the dependencies and next run the build command:

~~~bash
npm install
npm run build
~~~

This will put the built frontend into the `/dist` folder.

### Clone the backend
~~~bash
git clone https://gitlab+deploy-token-158:gldt-rcirz95SsXUDEQTkpDXS@ifs.dfki.de/software-hub/opc-ua/vue-module-ui/module-ui-backend.git
~~~

Remember to switch branches:
~~~bash
git switch 25.06.0-dev
~~~

### Copy to the backend
Take everything from within the `/dist` folder of the frontend and put it into `/public` within the backend project.
You can delete the `dummy.json` already present in that folder.

### Build the container
> [!note]
> You need to have [Docker](https://docs.docker.com/engine/install/) installed

To build the container, run: 

~~~bash
docker build --build-arg INFO_IMAGE_TAG=25.06.0-local -t local-module-ui:25.06.0-local .
~~~

The versions should match the branches used previously. 

Now the image should be available locally. Please refer to [/dist/docker/module-ui](https://ifs.dfki.de/dist/docker/module-ui) about how to use/run it.