# shoespic
shoespic assesments

## docker build
$ docker build -t checkiam:dev .

## docker run with env (configure .env, need access keys!!)
$ docker run -d --env-file ./.env --name checkiam -p 5000:80 checkiam:dev


## view Swagger UI
$ open http://127.0.0.1:5000/docs


## Dev command 
$ uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload