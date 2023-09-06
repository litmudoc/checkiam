# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
from datetime import datetime, timezone
import boto3
from fastapi import FastAPI, Query

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


def convert_seconds(seconds):  # 초를 입력 받아 사람이 보기 좋은 포맷으로 변환 합니다
    days, seconds = divmod(seconds, 86400)  # 일수 변환
    hours, seconds = divmod(seconds, 3600)  # 시간 변환
    minutes, seconds = divmod(seconds, 60)  # 분 변환
    readable = []
    if days > 0:
        readable.append(f"{days} Days")
    if hours > 0:
        readable.append(f"{hours} Hours")
    if minutes > 0:
        readable.append(f"{minutes} Mins")
    if seconds > 0:
        readable.append(f"{seconds} Seconds")
    if readable:
        result = ", ".join(readable)
    else:
        result = "0 Second"
    return result


def keys_filter(username, arn, age_seconds):  # 입력된 시간보다 오래된 키 정보를 반환합니다.
    try:
        user_info = {}
        user_key_list = iam_client.list_access_keys(UserName=username)
        if user_key_list:
            for key in user_key_list['AccessKeyMetadata']:
                create_key_date = key['CreateDate']
                age = now - create_key_date
                diffrence_age = int(age.total_seconds())
                if diffrence_age >= int(age_seconds):
                    # 기간이 지난 IAM Access Key의 정보 저장.
                    user_info = {
                        "access_key_id": key['AccessKeyId'],
                        "user_name": username,
                        "user_arn": arn,
                        "created_key_date": create_key_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "created_key_hours": diffrence_age // 3600,
                        "created_key_desc": f"It created {convert_seconds(diffrence_age)} ago!!"
                    }
    except Exception as e:
        print(f"IAM 사용자 {username}의 Access Key를 가져올 수 없습니다. 오류: {str(e)}")
    return user_info


# 인수가 없으면 기본값을 90일(777600초)이 지난 키를 가져오도록 실행 합니다.
def get_users_old_access_keys(age_seconds=7776000):
    try:
        old_keys_info = []
        response = iam_client.list_users()
        users = response['Users']
        for user in users:
            username = user['UserName']
            user_key_info = keys_filter(username, user['Arn'], age_seconds)
            if user_key_info:
                old_keys_info.append(user_key_info)
    except Exception as e:
        print(f"IAM 사용자 목록을 가져올 수 없습니다. 오류: {str(e)}")
    return old_keys_info


@app.get("/old-key-age/")  # 쿼리가 없으면 None을 기본값으로 합니다.
async def list_old_access_keys(
        days: int = Query(None, title="Days", description="Number of days"),
        hours: int = Query(None, title="Hours", description="Number of hours"),
        mins: int = Query(None, title="Mins", description="Number of mins"),
        seconds: int = Query(None, title="Seconds",
                             description="Number of seconds")
):
    age_seconds = 0
    input_times = [days, hours, mins, seconds]
    conversions = [86400, 3600, 60, 1]  # 일, 시간, 분, 초의 변환값
    # 쿼리로 받아온 값이 있으면 모두 초로 변환해서 더합니다.
    for unit, conversion in zip(input_times, conversions):
        if unit is not None:
            age_seconds += unit * conversion
    old_keys_info = get_users_old_access_keys(age_seconds)
    return {"old_created_keys": old_keys_info}

if __name__ == '__main__':
    try:
        old_keys_info = get_users_old_access_keys()
        print({"old_created_keys": old_keys_info})
    except Exception as e:
        print(f"IAM 사용자 목록을 가져올 수 없습니다. 오류: {str(e)}")
