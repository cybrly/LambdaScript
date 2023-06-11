import requests
import json
import sys
import os
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
SSH_KEY_NAMES = os.getenv('SSH_KEY_NAMES')
SSH_KEY_PATH = os.getenv('SSH_KEY_PATH')


API_URL = "https://cloud.lambdalabs.com/api/v1/"

def colored_print(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")

def get_instances_availability(print_info=True):
    response = requests.get(API_URL + "instance-types", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]
    available_instances = {}
    unavailable_instances = []
    
    for idx, (instance_type, instance_info) in enumerate(data.items(), start=1):
        formatted_instance_type = ' '.join(part.capitalize() for part in instance_type.replace('gpu_', '').split('_'))
        if instance_info["regions_with_capacity_available"]:
            if '8x' in instance_type:
                formatted_instance_type = f"{Fore.GREEN}{formatted_instance_type}{Style.RESET_ALL}"
            available_instances[idx] = {
                "name": instance_type,
                "region": next(iter(instance_info["regions_with_capacity_available"]))
            }
        else:
            unavailable_instances.append(f"{idx}. {formatted_instance_type}")
    
    if print_info:
        colored_print("\nAvailable", Fore.GREEN)
        for number, info in available_instances.items():
            print(f"{number}. {info['name']}")
        colored_print("\nUnavailable", Fore.RED)
        for instance in unavailable_instances:
            print(instance)
    
    return available_instances

def start_instance(number):
    instance_info = get_instances_availability(print_info=False).get(number)
    if instance_info is None:
        colored_print(f"\nThe number you provided does not correspond to an available GPU. Try again.", Fore.RED)
        sys.exit(1)

    data = {
        # Assume the region info is a dictionary and use the 'name' field
        "region_name": instance_info["region"]['name'],
        "instance_type_name": instance_info["name"],
        "ssh_key_names": SSH_KEY_NAMES.split(',')
    }

    response = requests.post(API_URL + "instance-operations/launch", headers={"Authorization": f"Bearer {AUTH_TOKEN}"}, json=data)
    if response.status_code == 200:
        colored_print(f"\nGPU instance started successfully.", Fore.GREEN)
    else:
        error_response = response.json()
        colored_print(f"\nFailed to start GPU instance. Error Code: {error_response['error']['code']}, Error Message: {error_response['error']['message']}", Fore.RED)

def check_running_instances():
    response = requests.get(API_URL + "instances", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]
    if not data:
        colored_print(f"\nThere are no instances currently running. \n",Fore.RED)
        return

    for instance in data:
        if instance['status'] == 'active':
            instance_type = ' '.join(part.capitalize() for part in instance['instance_type']['name'].replace('gpu_', '').split('_'))
            print(f"\n{Fore.BLUE}Instance ID:{Style.RESET_ALL} {instance['id']}")
            print(f"{Fore.BLUE}Instance Type:{Style.RESET_ALL} {instance_type}")
            print(f"{Fore.BLUE}IP Address:{Style.RESET_ALL} {instance['ip']}")
            print(f"{Fore.BLUE}Status:{Fore.GREEN} {instance['status']}{Style.RESET_ALL}\n")

def stop_instance(instance_id):
    url = API_URL + "instance-operations/terminate"
    payload = {"instance_ids": [instance_id]}
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        colored_print(f"\nInstance terminated successfully.",Fore.GREEN)
    else:
        error_code = response.json()["error"]["code"]
        colored_print(f"\nFailed to terminate instance. Error Message: {error_code}",Fore.RED)

def connect_instance(instance_id):
    # Get the instance information
    response = requests.get(API_URL + "instances", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]

    for instance in data:
        if instance['id'] == instance_id and instance['status'] == 'active':
            os.system(f"ssh -i {SSH_KEY_PATH} ubuntu@{instance['ip']}")
            break
    else:
        colored_print(f"\nNo active instance found with id: {instance_id}", Fore.RED)

def print_help_menu():
    help_text = """
    USAGE:
        python lambda.py [COMMAND] [ARGUMENT]

    COMMANDS:
        list                    List all available GPU instances.
        check                   Check the status of running instances.
        start <number>          Start a GPU instance with the given number.
        stop <instance_id>      Terminate the instance with the given instance id.
        connect <instance_id>   Open an SSH connection to the instance with the given instance id.

    """
    print(help_text)

def main():
    if len(sys.argv) < 2 or sys.argv[1].lower() in ["-h", "--help"]:
        print_help_menu()
        sys.exit(0)

    command = sys.argv[1].lower()
    if command == "check":
        check_running_instances()
    elif command == "start":
        if len(sys.argv) < 3:
            print(f"\nMissing parameters for 'start'. Use 'start <number>'")
            sys.exit(1)
        start_instance(int(sys.argv[2]))
    elif command == "stop":
        if len(sys.argv) < 3:
            print(f"\nMissing parameters for 'stop'. Use 'stop <instance_id>'")
            sys.exit(1)
        stop_instance(sys.argv[2])
    elif command == "list":
        get_instances_availability()
    elif command == "connect":
        if len(sys.argv) < 3:
            print(f"\nMissing parameters for 'connect'. Use 'connect <instance_id>'")
            sys.exit(1)
        connect_instance(sys.argv[2])  # Now this line is correctly indented
    else:
        print(f"\nUnknown command: {command}. Use 'check', 'start', 'stop', 'list', or 'connect'")
        sys.exit(1)

if __name__ == "__main__":
    main()
