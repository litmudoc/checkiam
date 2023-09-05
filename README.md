# shoespic
shoespic assesments

## docker build
$ docker build -t checkiam:dev .

## docker run with env (configure .env, need access keys!!)
$ docker run -d --env-file ./.env --name checkiam -p 5000:80 checkiam:dev

## Dev command 
$ uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload


## view Swagger UI
$ open http://127.0.0.1:5000/docs

$ curl -X 'POST' \
  'http://127.0.0.1:5000/old-key-age?days=90' \
  -H 'accept: application/json' \
  -d ''