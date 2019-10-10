# Word Count

## Deployment Notes

### Heroku Steps

First add ssh keys for authentication to heroku with
`heroku keys:add`. Check if keys exist with `heroku keys`.

Then for each of stage and pro (production):
```cmd
heroku create jh-wordcount-stage
git remote add stage git@heroku.com:jh-wordcount-stage.git
git push stage master
```
