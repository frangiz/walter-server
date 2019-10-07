# Walter server
[![Build Status](https://travis-ci.com/frangiz/walter-server.svg?branch=master)](https://travis-ci.com/frangiz/walter-server)
[![Build Status](https://img.shields.io/github/license/frangiz/walter-server.svg)](https://img.shields.io/github/license/frangiz/walter-server.svg)

The server for Walter written in Python.

## Database

### After a complete reset of the database
`flask db init`

### Create migration files after the models have been changed
`flask db migrate -m "<message>`

### Upgrade a database
`flask db upgrade`