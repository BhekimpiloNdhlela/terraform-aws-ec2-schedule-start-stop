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
MS_TEAMS_REPORTING_ENABLED = os.environ.get("MS_TEAMS_REPORTING_ENABLED", "false").lower() == "true"
MS_TEAMS_WEBHOOK_URL = os.environ.get("MS_TEAMS_WEBHOOK_URL")


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

def get_ec2_instance_ids_by_schedule_tag(tag_key, tag_value):
    """
    List EC2 instances filtered by a specific tag key and value.
    
    :param tag_key: The key of the tag to filter instances by (e.g., 'auto-start').
    :param tag_value: The value of the tag to filter instances by (e.g., 'true' or 'false').
    :return: A list of dictionaries containing instance IDs and tags.
    """
    instance_ids = []

    paginator = ec2_client.get_paginator('describe_instances')
    page_iterator = paginator.paginate()

    for page in page_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                tags = instance.get('Tags', [])
                
                # check if the instance has the specified tag with the desired value
                for tag in tags:
                    if tag['Key'] == tag_key and tag['Value'].lower() == tag_value.lower():
                        instance_ids.append(instance['InstanceId'])
                        # no need to check further tags for this instance
                        break
    return instance_ids


def stop_ec2_instance(ec2_instanceIds) -> None:
    """
    Stops an EC2 instance.

    Args:
        instance_id (str): The ID of the EC2 instance to stop.
        failed_instances (List[str]): A list to collect IDs of instances that failed to stop.

    Returns:
        None
    """
    try:
        ec2_client.stop_instances(InstanceIds=ec2_instanceIds)
        print(f"[INFO]: Successfully stopped instance(s): '{ec2_instanceIds}'.")
    except Exception as e:
        raise Exception(f"[ERROR]: Failed to start instance {ec2_instanceIds}: {str(e)}")

def start_ec2_instance(ec2_instanceIds) -> None:
    """
    Starts an EC2 instance.

    Args:
        instance_id (str): The ID of the EC2 instance to start.
        failed_instances (List[str]): A list to collect IDs of instances that failed to start.

    Returns:
        None
    """
    try:
        ec2_client.start_instances(InstanceIds=ec2_instanceIds)
        print(f"[INFO]: Successfully started instance(s): '{ec2_instanceIds}'.")
    except Exception as e:
        raise Exception(f"[ERROR]: Failed to start instance {ec2_instanceIds}: {str(e)}")

def handler(event, context):
    """
    AWS Lambda handler to start or stop EC2 instances based on the action in the event.
    """
    print(f"Lambda triggered with event: {event}")

    # get action and validate if it they are valid actions. 
    action = event.get('action')
    if action not in ["start", "stop"]:
        raise Exception("[ERROR]: Invalid action provided. Must be 'start' or 'stop'.")
    
    try:
        if action == "start":
            instance_ids = get_ec2_instance_ids_by_schedule_tag(tag_key, tag_value)
            start_ec2_instance(instance_ids)
            success_message = f"[INFO]: Successfully started EC2 instances: {'\n'.join([])}"
            log_and_report_process_results(False, success_message)
        elif action == "stop":
            instance_ids = get_ec2_instance_ids_by_schedule_tag(tag_key, tag_value)
            stop_ec2_instance(instance_ids)
            success_message = f"[INFO]: Successfully stopped EC2 instances: {'\n'.join([])}"
            log_and_report_process_results(False, success_message)
    except Exception as e:
        log_and_report_process_results(True, str(e))



    # tag_key, tag_value = 'auto-start', 'True'
    