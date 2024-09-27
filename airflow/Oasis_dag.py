from airflow import DAG
from airflow.decorators import task
from dotenv import load_dotenv
import os
from airflow.operators.bash import BashOperator
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import get_current_context
from datetime import datetime, timedelta
import json, requests

from Oasis_category_info import *


# 함수 정의: HTTP POST 요청
def send_post_request(categoryId):
    load_dotenv()
    url = os.getenv("OASIS_SERVICE_URL")

    response = requests.post(url)

    # 응답 코드와 내용을 로그로 남김
    if response.status_code == 200:
        print(f"Success: {response.json()}")
    elif "500 Internal Server Error" in response.text:
        context = get_current_context()
        print(
            f"Failed: {response.status_code}, NO PRODUCT EXISTS, detail shows below\n{response.text}"
        )
        raise AirflowSkipException(f"Skip task {context['ti'].task_id}")
    else:
        print(f"Failed: {response.status_code}, {response.text}")
        response.raise_for_status()


# DAG의 기본 설정
default_args = {
    "owner": "khuda",  # DAG 소유자
    "depends_on_past": False,  # 이전 DAG 실패 여부에 의존하지 않음
    #    'email': ['dbgpwl34@gmail.com'],    # 수신자 이메일
    #    "email_on_success": True,           # 성공 시 이메일 전송
    #    'email_on_failure': True,           # 실패 시 이메일 전송
    #    'email_on_retry': True,             # 재시도 시 이메일 전송
    "retries": 1,  # 실패 시 재시도 횟수
    "retry_delay": timedelta(minutes=5),  # 재시도 간격
}

# DAG 정의
with DAG(
    "Oasis_Crawling_DAG",  # DAG의 이름
    default_args=default_args,  # 기본 인자 설정
    description="Oasis Crawling",  # DAG 설명
    schedule_interval="0 * * * *",
    start_date=datetime(2024, 9, 20),  # 시작 날짜
    catchup=False,  # 시작 날짜부터 현재까지의 미실행 작업 실행 여부
) as dag:

    @task
    def send_post_request_OASIS_task():
        return send_post_request()

    # TaskFlow API로 task 정의
    @task
    def generate_queue_values():
        return [{"consumer": "Oasis.product.queue"}]

    # BashOperator에서 expand로 받은 값을 사용
    run_consumer_task = BashOperator.partial(
        task_id="run-consumer-task",
        bash_command="python3 /home/patturning1/homeplus_consumer.py {{ params.consumer }}",  # 템플릿을 사용하여 매핑된 값 사용
    ).expand(params=generate_queue_values())

    [
        run_consumer_task,
        send_post_request_OASIS_task.expand(),
    ]
