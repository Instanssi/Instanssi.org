Instanssi.org store frontend
============================

This is the store frontend for the Instanssi.org website. It is a Vue 3 app
bundled as an IIFE that runs on the Django-served store page. Vue itself is
loaded as a global from a static file; the bundle does not include it.

Dependencies:
- node 24 LTS
- pnpm 10.x

Commands:

    pnpm install   # install dependencies
    pnpm run build # build bundle to backend static dir
    pnpm run dev   # start vite dev server
    pnpm run test  # run tests
