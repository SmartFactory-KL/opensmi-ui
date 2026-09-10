# Vue Module UI Frontend
Simple frontend for Module UI

## Prerequisites
You need to have [nodeJS 20](https://nodejs.org/en/download/package-manager/current) installed. Check using:

```bash
node --version
```


## Installation
To install, clone this repository and run 

```bash
npm install
```

This might take a while and only has to be done once.

## Run
To run, use: 

```bash
npm run dev
```

which will run a development server serving the frontend at `localhost:5173` with hot-reloading enabled.
It expects the module-ui-backend to be running at `localhost:8000` (check at [vite.config.ts](vite.config.ts))