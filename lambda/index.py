import boto3
import os
import json
from typing import List, Dict
import requests

# Initialize AWS clients for EC2 and SNS
ec2_client = boto3.client("ec2")
sns_client = boto3.client("sns")

# Retrieve SNS Topic ARN and EC2 Instance IDs from environment variables
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
EC2_INSTANCE_IDS = os.environ.get("EC2_INSTANCE_IDS").split(',')
TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL")

def send_message_to_teams(message: str) -> None:
    """
    Sends a message to a Microsoft Teams channel using an incoming webhook.

    Parameters:
    - message (str): The message to send to the Teams channel.

    Returns:
    None
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "text": message
    }

    try:
        response = requests.post(TEAMS_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"Message sent to Teams successfully: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Teams: {e}")

def stop_ec2_instance(instance_id: str, failed_instances: List[str]) -> None:
    """
    Attempts to stop an EC2 instance and appends the instance ID to the failed_instances
    list if an error occurs.

    Parameters:
    - instance_id (str): The ID of the EC2 instance to stop.
    - failed_instances (List[str]): A list to collect IDs of instances that failed to stop.

    Returns:
    None
    """
    try:
        ec2_client.stop_instances(InstanceIds=[instance_id])
        print(f"Successfully stopped instance: '{instance_id}'.")
    except Exception as e:
        error_message = f"Failed to stop instance {instance_id}: {str(e)}"
        print(error_message)
        failed_instances.append(instance_id)

def start_ec2_instance(instance_id: str, failed_instances: List[str]) -> None:
    """
    Attempts to start an EC2 instance and appends the instance ID to the failed_instances
    list if an error occurs.

    Parameters:
    - instance_id (str): The ID of the EC2 instance to start.
    - failed_instances (List[str]): A list to collect IDs of instances that failed to start.

    Returns: 
    None
    """
    try:
        ec2_client.start_instances(InstanceIds=[instance_id])
        print(f"Successfully started instance: '{instance_id}'.")
    except Exception as e:
        error_message = f"Failed to start instance {instance_id}: {str(e)}"
        print(error_message)
        failed_instances.append(instance_id)

def send_error_notification(failed_instances: List[str]) -> None:
    """
    Sends an SNS notification if there are any failed EC2 instance operations.

    Parameters:
    - failed_instances (List[str]): A list of EC2 instance IDs that failed to stop/start.

    Returns:
    None
    """
    if not failed_instances:
        return  # No failures, so no need to send an email
    
    error_message = (
        "The following EC2 instances failed to stop or start:\n" +
        "\n".join(failed_instances)
    )
    
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EC2 Instance Stop/Start Errors",
            Message=error_message
        )
        print("SNS notification sent successfully")
    except Exception as sns_error:
        print(f"Failed to send SNS notification: {sns_error}")

def lambda_handler(event, context):

    print(f"Lambda triggered successfully")
    action = event.get('detail', {}).get('action')

    try:
        if action == 'start':
            ec2_client.start_instances(InstanceIds=[EC2_INSTANCE_ID])
            message = f"EC2 instance {EC2_INSTANCE_ID} started successfully."
            print(message)
            send_error_notification("EC2 Start Success", message)

        elif action == 'stop':
            ec2_client.stop_instances(InstanceIds=[EC2_INSTANCE_ID])
            message = f"EC2 instance {EC2_INSTANCE_ID} stopped successfully."
            print(message)
            send_error_notification("EC2 Stop Success", message)

        else:
            print("Unknown action received.")
    except Exception as e:
        error_message = f"Error occurred while performing {action} on EC2 instance {EC2_INSTANCE_ID}: {str(e)}"
        print(error_message)
        send_sns_message("EC2 Action Error", error_message)
