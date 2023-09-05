# # Intro

AWS IAM User들의 주어진 만료일이 지난 Access Key 리스트를 확인하는 API 서버 입니다.

API 서버는 Python으로 작성되었으며 아래 환경에서 작성 및 테스트 되었습니다.

* MacOS Big Sur 11.7.9 (Intel)
* Docker Desktop 4.21.1 (114176)
  * Kubernetes: v1.27.2
* Python 3.9.16 (x86)
  * boto3 1.28.40
  * FastAPI 0.92.0
  * Pydantic 1.10.12
  * Uvicorn 0.20.0

----------------------

## # Prerequisite
다음 환경에서 `Docker` 또는 `Kubernetes`에 배포 할 수 있도록 배포(Deploy) 방법을 설명 합니다.

* `MacOS` 또는 `Linux` 환경이 구성되어 있어야 합니다.
* `AWS Access Key`, `Secret Key`가 준비 되어 있어야 합니다.
* `docker` 명령어가 사용 가능해야 합니다. (도커 컨테이너의 생성이 가능해야 합니다.)
* `kubectl` 명령어가 사용 가능해야 합니다. (쿠버네티스에 배포가 가능해야 합니다.)
* `python3`, `git`, `base64`, `sed`, `awk`, `curl`, `open` 등의 명령어가 사용 가능해야 합니다.

----------------------

## # :one: Docker Deploy
<ul>

### 1. Source download
소스를 다운로드 받습니다.
```bash
~ $ git clone https://github.com/litmudoc/shoespic.git
~ $ cd shoespic
~/shoespic $
```
### 2. AWS API Key configure
준비된 AWS Access Key와 Secret Key를 프로젝트 루트에 `.env` 파일로 저장합니다.
```bash
## 따옴표와 공백이 들어가지 않도록 주의 하세요. (에러가 나실꺼에요!!)
~/shoespic $ cat <<EOF >.env
AWS_ACCESS_KEY_ID=___{{Replace AWS Access Key}}___
AWS_SECRET_ACCESS_KEY=___{{Replace AWS Secret Key}}___
AWS_DEFAULT_REGION=___{{Replace AWS Default region}}___
EOF
```

### 3. Docker Image build
도커 이미지를 생성하고 확인합니다.
```bash
~/shoespic $ docker build -t checkiam:dev .
~/shoespic $ docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
checkiam     dev       8c34269b42b9   4 minutes ago   260MB
```

### 4. deploy Docker container (with .env)
생성된 이미지와 환경변수로 컨테이너를 생성하고 확인합니다.
```bash
~/shoespic $ docker run -d --env-file ./.env --name checkiam -p 30080:5000 checkiam:dev
~/shoespic $ docker ps         
CONTAINER ID   IMAGE          COMMAND                   CREATED          STATUS          PORTS                     NAMES
fba77de791de   checkiam:dev   "uvicorn app.main:ap…"   5 minutes ago   Up 5 minutes   0.0.0.0:30080->5000/tcp   checkiam
```

### 5. API 서버의 정상동작 여부를 확인 합니다.
<ul>

#### Use: `curl` command

```bash
~/shoespic $ curl -X 'GET' \
  'http://127.0.0.1:30080/old-key-age?days=90' \
  -H 'accept: application/json'
```

#### Use: Swagger UI
Swagger Web UI에서 `/old-key-age` api를 테스트(Try it out) 합니다. 
``` bash
~/shoespic $ open http://127.0.0.1:30080/docs#/default/list_old_access_keys_old_key_age_get
```

#### Response: Body
`days`를 `90`으로 요청시 JSON형식으로 90일 이상된 Key들의 정보를 반환 합니다.
```json
{
  "old_created_keys": [
    {
      "access_key_id": "************************",
      "user_name": "******",
      "user_arn": "arn:aws:iam::************:user/******",
      "create_key_date": "2021-06-14 10:00:35",
      "create_key_age": 812,
      "create_key_desc": "It created 812 days ago!!"
    },
    ...
    {
    ...
    }
  ]
}
```

</ul>

### 6. Docker Cleanup
도커 컨테이너와 이미지를 삭제 합니다.
```bash
~/shoespic $ docker stop checkiam
~/shoespic $ docker rm checkiam
~/shoespic $ docker rmi checkiam:dev
```

</ul>

----------------------

## # :two: K8s Deploy

<ul>

### 1. Source download
소스를 다운로드 받습니다.
```bash
~ $ git clone https://github.com/litmudoc/shoespic.git
~ $ cd shoespic
~/shoespic $
```
### 2. AWS API Key configure
준비된 AWS Access Key와 Secret Key를 프로젝트 루트에 `.env` 파일로 저장합니다.
```bash
## 따옴표와 공백이 들어가지 않도록 주의 하세요. (에러가 나실꺼에요!!)
~/shoespic $ cat <<EOF >.env
AWS_ACCESS_KEY_ID=___{{Replace AWS Access Key}}___
AWS_SECRET_ACCESS_KEY=___{{Replace AWS Secret Key}}___
AWS_DEFAULT_REGION=___{{Replace AWS Default region}}___
EOF
```

### 3. Docker Image build
도커 이미지를 생성하고 확인합니다.
```bash
~/shoespic $ docker build -t checkiam:dev .
~/shoespic $ docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
checkiam     dev       8c34269b42b9   4 minutes ago   260MB
```

### 4. Deploy k8s deployment (with .env)
k8s에 배포될때 민감정보가 노출되지 않도록 스크립트로 배포 합니다.
```bash
~/shoespic $ sed "s#___AWS_ACCESS_KEY_ID___#`awk -F '=' '/AWS_ACCESS_KEY_ID/ {print $2}' ./.env | base64`#g" ./deploy/checkiam.yaml| \
sed "s#___AWS_SECRET_ACCESS_KEY___#`awk -F '=' '/AWS_SECRET_ACCESS_KEY/ {print $2}' ./.env | base64`#g" | \
sed "s#___AWS_DEFAULT_REGION___#`awk -F '=' '/AWS_DEFAULT_REGION/ {print $2}' ./.env | base64`#g" | \
kubectl apply -f -
```

### 5. API 서버의 정상동작 여부를 확인 합니다.
<ul>

#### Use: `curl` command

```bash
~/shoespic $ curl -X 'GET' \
  'http://127.0.0.1:30080/old-key-age?days=90' \
  -H 'accept: application/json'
```

#### Use: Swagger UI
Swagger Web UI에서 `/old-key-age` api를 테스트(Try it out) 합니다. 
``` bash
~/shoespic $ open http://127.0.0.1:30080/docs#/default/list_old_access_keys_old_key_age_get
```

#### Response: Body
`days`를 `90`으로 요청시 JSON형식으로 90일 이상된 Key들의 정보를 반환 합니다.
```json
{
  "old_created_keys": [
    {
      "access_key_id": "************************",
      "user_name": "******",
      "user_arn": "arn:aws:iam::************:user/******",
      "create_key_date": "2021-06-14 10:00:35",
      "create_key_age": 812,
      "create_key_desc": "It created 812 days ago!!"
    },
    ...
    {
    ...
    }
  ]
}
```

</ul>

### 6. K8s Cleanup
배포된 쿠버네티스 리소스와 도커 이미지를 삭제 합니다.
```bash
~/shoespic $ kubectl delete -f deploy/checkiam.yaml
~/shoespic $ docker rmi checkiam:dev

```

</ul>

----------------------
# # :fire: Development

* `!! 주의 !!` 리포지터리에 Access, Secret Key 등의 보안 정보가 저장되지 않도록 하세요.
* `.gitignore`에서 보안키가 저장된 `.env`가 무시 되도록 합니다.

<ul>

## 1. Source Clone

* github 에서 소스를 다운로드 받습니다.
```bash
~ $ cd ~
~ $ git clone https://github.com/litmudoc/shoespic.git
~ $ cd shoespic
```

## 2. Python Lib Install

* 필요 Python 라이브러리를 설치 합니다.
```bash
~/shoespic $ pip install -r requirements.txt
```


## 3. AWS API Key configure
* 준비된 AWS Access Key와 Secret Key를 프로젝트 루트에 `.env` 파일로 저장합니다.

```bash
## 따옴표와 공백이 들어가지 않도록 주의 하세요. (에러가 나실꺼에요!!)
~/shoespic $ cat <<EOF >.env
AWS_ACCESS_KEY_ID=___{{Replace AWS Access Key}}___
AWS_SECRET_ACCESS_KEY=___{{Replace AWS Secret Key}}___
AWS_DEFAULT_REGION=___{{Replace AWS Default region}}___
```

* Gunicorn 웹서버를 실행합니다. (개발모드로!!)
```bash
~/shoespic $ uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

## 4. API Test
<ul>

## `curl` 로 테스트 합니다.

```bash
~/shoespic $ curl -X 'GET' \
  'http://127.0.0.1:5000/old-key-age?days=90' \
  -H 'accept: application/json'
```

## Swagger 웹 UI로 테스트 합니다.
- Swagger Web UI에서 `/old-key-age` api를 테스트(Try it out) 합니다. 

```bash
~/shoespic $ open http://127.0.0.1:5000/docs
```

## Response: Body
* `days`를 `90`으로 요청시 JSON형식으로 90일 이상된 Key들의 정보를 반환 합니다.
```json
{
  "old_created_keys": [
    {
      "access_key_id": "************************",
      "user_name": "******",
      "user_arn": "arn:aws:iam::************:user/******",
      "create_key_date": "2021-06-14 10:00:35",
      "create_key_age": 812,
      "create_key_desc": "It created 812 days ago!!"
    },
    ...
    {
    ...
    }
  ]
}
```

</ul>

----------------------

# :fire: TODO... :dart:
:) :) :) :) :)

----------------------

</ul>