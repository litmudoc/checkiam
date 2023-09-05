# shoespic
shoespic assesments

## Dev command 
$ uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
## Dev Swagger UI
$ open http://127.0.0.1:5000/docs

## docker build
$ docker build -t checkiam:dev .

## docker run with env (configure .env, need access keys!!)
$ docker run -d --env-file ./.env --name checkiam -p 30080:5000 checkiam:dev

## Docker Swagger UI
$ open http://127.0.0.1:30080/docs

## curl api access command 
$ curl -X 'POST' \
  'http://127.0.0.1:30080/old-key-age?days=90' \
  -H 'accept: application/json' \
  -d ''

## K8S Deploy
sed "s#___AWS_ACCESS_KEY_ID___#`awk -F '=' '/AWS_ACCESS_KEY_ID/ {print $2}' ./.env | base64`#g" ./deploy/checkiam.yaml| \
sed "s#___AWS_SECRET_ACCESS_KEY___#`awk -F '=' '/AWS_SECRET_ACCESS_KEY/ {print $2}' ./.env | base64`#g" | \
sed "s#___AWS_DEFAULT_REGION___#`awk -F '=' '/AWS_DEFAULT_REGION/ {print $2}' ./.env | base64`#g" | \
kubectl apply -f -