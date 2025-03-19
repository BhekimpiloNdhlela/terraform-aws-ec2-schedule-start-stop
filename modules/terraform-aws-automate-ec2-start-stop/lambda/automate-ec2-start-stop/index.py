import boto3
import os
import json
from typing import List, Optional, Dict
import requests

# instantiate AWS Clients
ec2_client = boto3.client("ec2")
sns_client = boto3.client("sns")

# environment Variables
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
ERROR_EMAIL_SUBJECT = os.environ.get("ERROR_EMAIL_SUBJECT")
ERROR_EMAIL_HEADER = os.environ.get("ERROR_EMAIL_HEADER")
ERROR_EMAIL_FOOTER = os.environ.get("ERROR_EMAIL_FOOTER")
SUCCESS_EMAIL_SUBJECT = os.environ.get("SUCCESS_EMAIL_SUBJECT")
SUCCESS_EMAIL_HEADER = os.environ.get("SUCCESS_EMAIL_HEADER")
SUCCESS_EMAIL_FOOTER = os.environ.get("SUCCESS_EMAIL_FOOTER")
MS_TEAMS_REPORTING_ENABLED = os.environ.get("MS_TEAMS_REPORTING_ENABLED", "false").lower() == "true"
MS_TEAMS_WEBHOOK_URL = os.environ.get("MS_TEAMS_WEBHOOK_URL")
START_TAG_VALUE = os.environ.get("EC2_SCHEDULE_AUTO_START_VALUE")
STOP_TAG_VALUE = os.environ.get("EC2_SCHEDULE_AUTO_STOP_VALUE")
START_TAG_KEY = os.environ.get("EC2_SCHEDULE_AUTO_START_KEY")
STOP_TAG_KEY = os.environ.get("EC2_SCHEDULE_AUTO_STOP_KEY")

def send_email_notification(subject: str, message: str) -> None:
    """
    Sends a notification via SNS using an email endpoint.

    Args:
        subject (str): The subject of the email notification.
        message (str): The body of the email notification.

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
        print(f"[ERROR]: Failed to send SNS notification: {e}")
        raise

def send_ms_teams_notification(message: str) -> None:
    """
    Sends a message to Microsoft Teams via a webhook.

    Args:
        message (str): The message to send to the Teams channel.

    Returns:
        None
    """
    print("[INFO]: Microsoft Teams reporting is enabled.")
    headers = {"Content-Type": "application/json"}
    payload = {"text": message}

    try:
        response = requests.post(MS_TEAMS_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"[INFO]: Message sent to Teams successfully. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR]: Failed to send message to Teams: {e}")
        raise

def log_and_report_process_results(error: bool, message: str) -> None:
    """
    Logs the process results and reports them via SNS and Microsoft Teams.

    Args:
        error (bool): Indicates whether the process encountered an error.
        message (str): The message to be logged and reported.

    Returns:
        None
    """
    print(f"[ERROR]: {message}" if error else f"[INFO]: {message}")

    formatted_message = ""
    if error:
        formatted_message = f"{ERROR_EMAIL_HEADER}\n{message}\n{ERROR_EMAIL_FOOTER}" 
    else:
        formatted_message = f"{SUCCESS_EMAIL_HEADER}\n{message}\n{SUCCESS_EMAIL_FOOTER}"

    send_email_notification(ERROR_EMAIL_SUBJECT if error else SUCCESS_EMAIL_SUBJECT, formatted_message)

    if MS_TEAMS_REPORTING_ENABLED:
        print("[INFO]: Microsoft Teams reporting is enabled.")
        send_ms_teams_notification(formatted_message)
    else:
        print("[INFO]: Microsoft Teams reporting is disabled.")

def get_ec2_instance_ids_by_schedule_tag(tag_key: str, tag_value: str) -> List[str]:
    """
    Retrieves EC2 instances that have a specific tag key and value.

    Args:
        tag_key (str): The key of the tag used to filter instances.
        tag_value (str): The value of the tag used to filter instances.

    Returns:
        List[str]: A list of instance IDs matching the tag key and value.
    """
    instance_ids = []
    paginator = ec2_client.get_paginator('describe_instances')
    page_iterator = paginator.paginate()

    for page in page_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                tags = instance.get('Tags', [])
                for tag in tags:
                    if tag['Key'] == tag_key and tag['Value'].lower() == tag_value.lower():
                        instance_ids.append(instance['InstanceId'])
                        # no need to check other tags if the instance matches the schedule tag
                        break
    return instance_ids

def stop_ec2_instances(instance_ids: List[str]) -> None:
    """
    Stops EC2 instances.

    Args:
        instance_ids (List[str]): A list of EC2 instance IDs to stop.

    Returns:
        None
    """
    if not instance_ids:
        print("[INFO]: No EC2 instances to stop.")
        return
    try:
        ec2_client.stop_instances(InstanceIds=instance_ids)
        print(f"[INFO]: Successfully stopped instances: {instance_ids}")
    except Exception as e:
        print(f"[ERROR]: Failed to stop instances {instance_ids}: {e}")
        raise

def start_ec2_instances(instance_ids: List[str]) -> None:
    """
    Starts EC2 instances.

    Args:
        instance_ids (List[str]): A list of EC2 instance IDs to start.

    Returns:
        None
    """
    if not instance_ids:
        print("[INFO]: No EC2 instances to start.")
        return
    try:
        ec2_client.start_instances(InstanceIds=instance_ids)
        print(f"[INFO]: Successfully started instances: {instance_ids}")
    except Exception as e:
        print(f"[ERROR]: Failed to start instances {instance_ids}: {e}")
        raise

def handler(event: Dict, context: Optional[Dict] = None) -> None:
    """
    AWS Lambda handler to start or stop EC2 instances based on the action in the event.

    Args:
        event (Dict): The event data passed to the Lambda function.
        context (Optional[Dict]): The context object passed to the Lambda function.

    Returns:
        None
    """
    print(f"[INFO]: Lambda triggered with event: {event}")
    action = event.get('action')
    if action not in ["start", "stop"]:
        print("[ERROR]: Invalid action provided. Must be 'start' or 'stop'.")
        raise ValueError("Invalid action provided. Must be 'start' or 'stop'.")

    try:
        instance_ids = []
        if action == "start":
            instance_ids = get_ec2_instance_ids_by_schedule_tag(START_TAG_KEY, START_TAG_VALUE)
            start_ec2_instances(instance_ids)
        elif action == "stop":
            instance_ids = get_ec2_instance_ids_by_schedule_tag(STOP_TAG_KEY, STOP_TAG_VALUE)
            stop_ec2_instances(instance_ids)

        success_message = f"Successfully {action}ed EC2 instances: {', '.join(instance_ids) if instance_ids else 'None'}"
        log_and_report_process_results(False, success_message)
    except Exception as e:
        log_and_report_process_results(True, str(e))
        raise
