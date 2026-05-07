# README

This is a frontend application for the [Instanssi.org](https://instanssi.org) APIs. It is intended to provide functionality similar to the venerable Kompomaatti:

- Browsing party events
- Posting compo entries
- Joining competitions
- Voting

Improvements over the original may or may not include:

- Faster navigation
- Mobile-friendly layout
- Full localization support

Made available under the terms of the MIT license. See LICENSE for details.

## Getting started

Clone the repository and copy `src/config.dist.ts` to `src/config.ts`. The example configuration should work when deploying the frontend to instanssi.org.

Get Node.js 8 LTS (or higher) and npm or yarn, and try building the application with:

    yarn&&yarn run build

This will download dependencies from npm / yarnpkg and try to build the application.

## Deploying

Copy the built files from `build/` to your web server and configure it to serve them under `/kompomaatti`.

The application uses HTML5 history manipulation for routing, so have the webserver serve the built `index.html` for any unknown files under that path.

## Developing

To start the development server, do:

    yarn run start

This will build and serve the frontend from your local machine, re-building and refreshing the page on any changes.

To emulate the intended production environment, the application is served under `http://localhost:8080/kompomaatti`. Other paths are proxied to `http://localhost:8000`, which is assumed to be the API and the rest of the site.

You can change the proxy target by setting the environment variable `INSTANSSI_URL`.

## Testing

The unit tests use Jest and Enzyme to test individual components in isolation. To run tests, try:

    yarn run test

You can leave the tests running in the background with:

    yarn run test:watch

When in watch mode, Jest will run tests related to files that have been changed in your git repository.
