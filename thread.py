import time
import threading
import json
import boto3

with open("data.json", "r") as file:
    credentials = json.load(file)
timer_started = False
s3 = boto3.client(
    "s3",
    aws_access_key_id=credentials["s3"]["aws_access_key_id"],
    aws_secret_access_key=credentials["s3"]["aws_secret_access_key"],
    region_name=credentials["s3"]["aws_default_region"],
)

my_bucket = "solutyics"
key_name = "s3_errorlogs"
file = "./error.log"

# The variable `file1` is storing the path to a file named "output.txt".
file1 = "./output.txt"
key_name1 = "necessory_data"


def fifteen_min_timer():
    while True:
        time.sleep(1800)  # 30 minutes in seconds (30 * 60 = 1800)
        s3.upload_file(file, my_bucket, key_name)
        s3.upload_file(file1, my_bucket, key_name1)

        print("success")


def start_timer():
    global timer_started
    if not timer_started:
        timer_thread = threading.Thread(target=fifteen_min_timer)
        timer_thread.daemon = True
        timer_thread.start()
        timer_started = True
