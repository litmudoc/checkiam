# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
from datetime import datetime, timezone
import boto3
from fastapi import FastAPI

# AWS 계정 정보 설정
try:
    # k8s secret 환경 변수 사용시 리턴이 입력되는 문제 => .strip("\n" 로 처리함
    aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"].strip("\n")
    aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"].strip("\n")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2").strip("\n")
except Exception as e:
    print(f"OS의 환경변수에서 Access key를 가져 올 수 없습니다. 오류: {str(e)}")

iam_client = boto3.client('iam', region_name=aws_region,
                          aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# 현재시간 비교시 timezone 정보가 없으면 date 계산시 에러가 발생. utc로 통일해요.
now = datetime.now(timezone.utc)

# API 서버 초기화.
app = FastAPI()


def keys_filter(username, arn, days):
    try:
        user_info = {}
        user_key_list = iam_client.list_access_keys(UserName=username)
        if user_key_list:
            for key in user_key_list['AccessKeyMetadata']:
                create_key_date = key['CreateDate']
                age = now - create_key_date
                if int(age.days) >= int(days):
                    # 기간이 지난 IAM Access Key의 정보 저장.
                    user_info = {
                        "access_key_id": key['AccessKeyId'],
                        "user_name": username,
                        "user_arn": arn,
                        "create_key_date": create_key_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "create_key_age": age.days,
                        "create_key_desc": f"It created {age.days} days ago!!"
                    }
    except Exception as e:
        print(f"IAM 사용자 {username}의 Access Key를 가져올 수 없습니다. 오류: {str(e)}")
    return user_info


def get_users_old_access_keys(days=90):
    try:
        old_keys_info = []
        response = iam_client.list_users()
        users = response['Users']
        for user in users:
            username = user['UserName']
            user_key_info = keys_filter(username, user['Arn'], days)
            if user_key_info:
                old_keys_info.append(user_key_info)
    except Exception as e:
        print(f"IAM 사용자 목록을 가져올 수 없습니다. 오류: {str(e)}")
    return old_keys_info


@app.post("/old-key-age")
async def list_old_access_keys(days: int):
    old_keys_info = get_users_old_access_keys(days)
    return {"old_created_keys": old_keys_info}

if __name__ == '__main__':
    try:
        old_keys_info = get_users_old_access_keys()
        print({"old_created_keys": old_keys_info})
    except Exception as e:
        print(f"IAM 사용자 목록을 가져올 수 없습니다. 오류: {str(e)}")
