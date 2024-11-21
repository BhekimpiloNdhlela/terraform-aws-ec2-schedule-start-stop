import boto3
import os
import json
from typing import List, Optional
import requests

ec2_client = boto3.client("ec2")
sns_client = boto3.client("sns")

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
ERROR_EMAIL_SUBJECT = os.environ.get("ERROR_EMAIL_SUBJECT")
ERROR_EMAIL_HEADER = os.environ.get("ERROR_EMAIL_HEADER")
ERROR_EMAIL_FOOTER = os.environ.get("ERROR_EMAIL_FOOTER")
SUCCESS_EMAIL_SUBJECT = os.environ.get("SUCCESS_EMAIL_SUBJECT")
SUCCESS_EMAIL_HEADER = os.environ.get("SUCCESS_EMAIL_HEADER")
SUCCESS_EMAIL_FOOTER = os.environ.get("SUCCESS_EMAIL_FOOTER")
EC2_INSTANCE_IDS = os.environ.get("EC2_INSTANCE_IDS", "")
MS_TEAMS_REPORTING_ENABLED = os.environ.get("MS_TEAMS_REPORTING_ENABLED", "false").lower() == "true"
MS_TEAMS_WEBHOOK_URL = os.environ.get("MS_TEAMS_WEBHOOK_URL")
EC2_INSTANCE_IDS_LIST = EC2_INSTANCE_IDS.split(",")


def send_email_notification(subject: str, message: str) -> None:
    """
    Sends a notification via SNS.

    Args:
        subject (str): The subject line for the SNS message.
        message (str): The body of the SNS message.

    Returns:
        None
    """
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message,
        )
        print("[INFO]: SNS notification sent successfully.")
    except Exception as e:
        raise Exception(f"[ERROR]: Failed to send SNS notification: {e}")

def send_ms_teams_notification(message: str) -> None:
    """
    Sends a message to Microsoft Teams via a webhook.

    Args:
        message (str): The message to send to the Teams channel.

    Returns:
        None
    """
    if not MS_TEAMS_REPORTING_ENABLED:
        print("[INFO]: Microsoft Teams reporting is disabled.")
        return

    headers = {"Content-Type": "application/json"}
    payload = {"text": message}

    try:
        response = requests.post(MS_TEAMS_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"[INFO]: Message sent to Teams successfully. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"[ERROR]: Failed to send message to Teams: {e}")

def log_and_report_process_results(error: bool, message: str) -> None:
    """
    Logs the process results and reports them via SNS and Microsoft Teams.

    Args:
        error (bool): Whether the process resulted in an error.
        message (str): The log message to report.

    Returns:
        None
    """
    print(message)

    if error: formatted_message = f"{ERROR_EMAIL_HEADER}\n{message}\n{ERROR_EMAIL_FOOTER}"
    else: formatted_message = f"{SUCCESS_EMAIL_HEADER}\n{message}\n{SUCCESS_EMAIL_FOOTER}"

    send_ms_teams_notification(formatted_message)
    send_email_notification(ERROR_EMAIL_SUBJECT if error else SUCCESS_EMAIL_SUBJECT, formatted_message)

def stop_ec2_instance() -> None:
    """
    Stops an EC2 instance.

    Args:
        instance_id (str): The ID of the EC2 instance to stop.
        failed_instances (List[str]): A list to collect IDs of instances that failed to stop.

    Returns:
        None
    """
    try:
        ec2_client.stop_instances(InstanceIds=EC2_INSTANCE_IDS_LIST)
        print(f"[INFO]: Successfully stopped instance: '{EC2_INSTANCE_IDS_LIST}'.")
    except Exception as e:
        raise Exception(f"[ERROR]: Failed to start instance {EC2_INSTANCE_IDS_LIST}: {str(e)}")

def start_ec2_instance() -> None:
    """
    Starts an EC2 instance.

    Args:
        instance_id (str): The ID of the EC2 instance to start.
        failed_instances (List[str]): A list to collect IDs of instances that failed to start.

    Returns:
        None
    """
    try:
        ec2_client.start_instances(InstanceIds=EC2_INSTANCE_IDS_LIST)
    except Exception as e:
        raise Exception(f"[ERROR]: Failed to start instance {EC2_INSTANCE_IDS_LIST}: {str(e)}")

def handler(event, context):
    """
    AWS Lambda handler to start or stop EC2 instances based on the action in the event.
    """
    print(f"Lambda triggered with event: {event}")

    try:
        if event.get('action') == "start":
            start_ec2_instance()
            success_message = f"[INFO]: Successfully started EC2 instances: {'\n'.join(EC2_INSTANCE_IDS_LIST)}"
            log_and_report_process_results(False, success_message)
        elif event.get('action') == "stop":
            stop_ec2_instance()
            success_message = f"[INFO]: Successfully stopped EC2 instances: {'\n'.join(EC2_INSTANCE_IDS_LIST)}"
            log_and_report_process_results(False, success_message)
    except Exception as e:
        log_and_report_process_results(True, str(e))
