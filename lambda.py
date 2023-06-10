import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
SSH_KEY_NAMES = os.getenv('ssh_key_names')

API_URL = "https://cloud.lambdalabs.com/api/v1/"

def print_in_color(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def get_available_instances():
    response = requests.get(API_URL + "instance-types", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]
    available_instances = []
    unavailable_instances = []
    for idx, (instance_type, instance_info) in enumerate(data.items(), start=1):
        formatted_instance_type = ' '.join(part.capitalize() for part in instance_type.replace('gpu_', '').split('_'))
        if instance_info["regions_with_capacity_available"]:
            if '8x' in instance_type:
                formatted_instance_type = f"\033[1;32m{formatted_instance_type}\033[0m"  # bold green
            available_instances.append(f"{idx}. {formatted_instance_type}")
        else:
            unavailable_instances.append(f"{idx}. {formatted_instance_type}")
            
    print_in_color("\nAvailable", "1;32")
    for instance in available_instances:
        print(instance)
    print_in_color("\nUnavailable", "1;31")
    for instance in unavailable_instances:
        print(instance)

def start_instance(number):
    gpu_dict = get_available_instances()
    if number not in gpu_dict:
        print("No GPU corresponds to that number. Please list GPUs first.")
        sys.exit(1)
    data = {
        "region_name": gpu_dict[number]["region"],
        "instance_type_name": gpu_dict[number]["name"],
        "ssh_key_names": os.getenv('SSH_KEY_NAMES')
    }
    response = requests.post(API_URL + "instance-operations/launch", headers={"Authorization": f"Bearer {AUTH_TOKEN}"}, json=data)
    if response.status_code == 200:
        print_in_color("GPU instance started successfully.", "1;32")
    else:
        print("Failed to start GPU instance.")

def stop_instance(instance_id):
    url = API_URL + "instance-operations/terminate"
    payload = {"instance_ids": [instance_id]}
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Instance terminated successfully.")
    else:
        print(f"Failed to terminate instance. Error: {response.text}")

def check_running_instances():
    response = requests.get(API_URL + "instances", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]
    if not data:
        print("\033[1;31;40m There are no instances currently running. \n")
        return

    for instance in data:
        if instance['status'] == 'active':
            instance_type = ' '.join(part.capitalize() for part in instance['instance_type']['name'].replace('gpu_', '').split('_'))
            print("\n\033[1;34;40m Instance ID: \033[0m" + instance['id'],
                  "\033[1;34;40m Instance Type: \033[0m" + instance_type,
                  "\033[1;34;40m IP Address: \033[0m" + instance['ip'],
                  "\033[1;34;40m Status: \033[1;32;40m" + instance['status'] + "\n", sep='\n')


def print_help_menu():
    help_text = """
    USAGE:
        python script_name.py [COMMAND] [ARGUMENT]

    COMMANDS:
        check               Check the status of running instances.
        start <number>      Start a GPU instance with the given number.
        stop <instance_id>  Terminate the instance with the given instance id.
        list                List all available GPU instances.

    """
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].lower() in ["-h", "--help"]:
        print_help_menu()
        sys.exit(0)

    command = sys.argv[1].lower()
    if command == "check":
        check_running_instances()
    elif command == "start":
        if len(sys.argv) < 3:
            print("Missing parameters for 'start'. Use 'start <number>'")
            sys.exit(1)
        start_instance(int(sys.argv[2]))
    elif command == "stop":
        if len(sys.argv) < 3:
            print("Missing parameters for 'stop'. Use 'stop <instance_id>'")
            sys.exit(1)
        stop_instance(sys.argv[2])
    elif command == "list":
        get_available_instances()
    else:
        print(f"Unknown command: {command}. Use 'check', 'start', 'stop' or 'list'")
        sys.exit(1)
