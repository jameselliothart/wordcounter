# Word Count

The (slightly dated) tutorial for this application can be found at:  
https://realpython.com/flask-by-example-part-1-project-setup/

View Stage here: https://jh-wordcount-stage.herokuapp.com  
View Production: https://jh-wordcount-pro.herokuapp.com

## Setup

On Ubuntu, need to install libpq-dev for psycopg2:  
`sudo apt-get install libpq-dev`

## Deployment Notes

### Docker

Postgres container setup:
```sh
docker pull postgres
mkdir -p $HOME/docker/volumes/wordcounter
docker run --rm --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/docker/volumes/wordcounter:/var/lib/postgresql/data postgres
docker exec -it pg-docker bash  # opens bash "inside" the container
psql -U postgres
```

Redis container setup:
```sh
docker run -d -p 6379:6379 --name wordcounter-redis redis
docker exec -it wordcounter-redis bash  # opens bash "inside" the container
redis-cli  # opens redis cli for testing, e.g. >ping responds PONG, >set name mark >get name responds "mark"
```

### Database Migrations

Migrations are handled by alembic via flask-migrate

Database migrations rely on the following environment variables:
* `APP_SETTINGS="config.DevelopmentConfig"` (this determines which configuration to use from `config.py`)
* `DATABASE_URL="postgresql://username:password@localhost/wordcount_dev"`

Migration steps after initializing with `flask db init`:
1. `flask db migrate -m "optional descriptive text"`
2. `flask db upgrade`

To upgrade the Heroku database, run:  
`heroku run flask db upgrade --app jh-wordcount-stage`

### Heroku Initial Setup

1. Install Heroku cli: https://devcenter.heroku.com/articles/heroku-cli
2. Log into Heroku: `heroku login`
3. Add ssh keys for authentication to heroku: `heroku keys:add`
    - Check if keys exist: `heroku keys`

Then for each of stage and pro (production):
```cmd
PS > heroku create jh-wordcount-stage
PS > git remote add stage git@heroku.com:jh-wordcount-stage.git
PS > git push stage master
```

### Heroku Environment Variables

To check existing heroku configs, run:
```cmd
PS > heroku config --app jh-wordcount-stage
=== jh-wordcount-stage Config Vars
APP_SETTINGS: config.StagingConfig
```

Configure application settings with:  
`heroku config:set APP_SETTINGS=config.StagingConfig --remote stage`

Add postgresql and set database configuration with:  
`heroku addons:create heroku-postgresql:hobby-dev --app jh-wordcount-stage`

Add redis and set redis url with:
`heroku addons:create redistogo:nano --app jh-wordcount-stage`

### Heroku Troubleshooting

View streaming logs with:
`heroku logs -t --remote stage`

To run heroku setup locally (activate virtualenv first and have .env file of environment configs):
`heroku local`