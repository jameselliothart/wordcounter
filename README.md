# Word Count

The (slightly dated) tutorial for this application can be found at:  
https://realpython.com/flask-by-example-part-1-project-setup/

View Stage here: https://jh-wordcount-stage.herokuapp.com  
View Production: https://jh-wordcount-pro.herokuapp.com

## Deployment Notes

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

First add ssh keys for authentication to heroku with
`heroku keys:add`. Check if keys exist with `heroku keys`.

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

Set database configuration with:  
`heroku addons:create heroku-postgresql:hobby-dev --app jh-wordcount-stage`

### Heroku Troubleshooting

View streaming logs with:
`heroku logs -t --remote stage`