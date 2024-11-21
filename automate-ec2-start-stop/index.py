import boto3
import os
import json
from typing import List
import requests

# Initialize AWS clients
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
        print("SNS notification sent successfully")
    except Exception as e:
        print(f"Failed to send SNS notification: {e}")


def send_ms_teams_notification(message: str) -> None:
    """
    Sends a message to Microsoft Teams via webhook.

    Args:
        message (str): The message to send to the Teams channel.

    Returns:
        None
    """
    if not MS_TEAMS_REPORTING_ENABLED:
        print("MS Teams reporting is disabled.")
        return

    headers = {"Content-Type": "application/json"}
    payload = {"text": message}

    try:
        response = requests.post(MS_TEAMS_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"Message sent to Teams successfully: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Teams: {e}")

def report_status(error, message):
    if error:
        send_email_notification(ERROR_EMAIL_SUBJECT, message)
        send_ms_teams_notification(message)
    else:
        send_email_notification(SUCCESS_EMAIL_SUBJECT, message)
        send_ms_teams_notification(message)

def stop_ec2_instance(instance_id: str, failed_instances: List[str]) -> None:
    """
    Stops an EC2 instance.

    Args:
        instance_id (str): The ID of the EC2 instance to stop.
        failed_instances (List[str]): A list to collect IDs of instances that failed to stop.

    Returns:
        None
    """
    try:
        ec2_client.stop_instances(InstanceIds=[instance_id])
        print(f"Successfully stopped instance: '{instance_id}'.")
    except Exception as e:
        failed_instances.append(instance_id)
        print(f"Failed to start instance {instance_id}: {str(e)}")


def start_ec2_instance(instance_id: str, failed_instances: List[str]) -> None:
    """
    Starts an EC2 instance.

    Args:
        instance_id (str): The ID of the EC2 instance to start.
        failed_instances (List[str]): A list to collect IDs of instances that failed to start.

    Returns:
        None
    """
    try:
        ec2_client.start_instances(InstanceIds=[instance_id])
        print(f"Successfully started instance: '{instance_id}'.")
    except Exception as e:
        failed_instances.append(instance_id)
        print(f"Failed to start instance {instance_id}: {str(e)}")

def handler(event, context):
    """
    AWS Lambda handler to start or stop EC2 instances based on the action in the event.
    """
    print(f"Lambda triggered with event: {event}")
    action, failed_instances = event.get('action'), []

    try:
        if action == "start":
            for instance_id in EC2_INSTANCE_IDS_LIST:
                start_ec2_instance(instance_id, failed_instances)
            success_message = f"Successfully started EC2 instances: {', '.join(EC2_INSTANCE_IDS_LIST)}"
            report_status(False, success_message)
        elif action == "stop":
            for instance_id in EC2_INSTANCE_IDS_LIST:
                stop_ec2_instance(instance_id, failed_instances)
            success_message = f"Successfully stopped EC2 instances: {', '.join(EC2_INSTANCE_IDS_LIST)}"
            report_status(False, success_message)
        else:
            print(f"[INFO]: Unknown action received: '{action}'")
            return
    except Exception as e:
        error_message = f"Error occurred during {action} action on EC2 instances: {EC2_INSTANCE_IDS_LIST}. Error: {str(e)}"
        report_status(True, error_message)

    if failed_instances:
        error_message = f"The following EC2 instances failed to {action}:\n" +"\n".join(failed_instances)
        report_status(True, error_message)