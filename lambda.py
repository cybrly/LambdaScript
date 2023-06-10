import requests
import json
import sys
import os
from dotenv import load_dotenv
from colorama import Fore, Back, Style

def colored_print(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")

load_dotenv()
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
SSH_KEY_NAMES = os.getenv('ssh_key_names')

API_URL = "https://cloud.lambdalabs.com/api/v1/"

def print_in_color(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def get_available_instances():
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
                "region": next(iter(instance_info["regions_with_capacity_available"]), 'us-west-2')
            }
        else:
            unavailable_instances.append(f"{idx}. {formatted_instance_type}")
            
    colored_print("\nAvailable", Fore.GREEN)
    for number, info in available_instances.items():
        print(f"{number}. {info['name']}")
    colored_print("\nUnavailable", Fore.RED)
    for instance in unavailable_instances:
        print(instance)
    
    return available_instances


def get_instance_info(number):
    response = requests.get(API_URL + "instance-types", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]
    instance_info = list(data.items())[number-1]  # Use number-1 to get the correct index
    instance_type = instance_info[0]
    instance_region = next(iter(instance_info[1]["regions_with_capacity_available"]), None)
    return {"name": instance_type, "region": instance_region}

def start_instance(number):
    gpu_info = get_instance_info(number)
    if not gpu_info["region"]:
        colored_print("The selected instance does not have an available region.", Fore.RED)
        sys.exit(1)
    data = {
        "region_name": str(gpu_info["region"]["name"]),
        "instance_type_name": gpu_info["name"],
        "ssh_key_names": os.getenv('SSH_KEY_NAMES').split(',')
    }
    response = requests.post(API_URL + "instance-operations/launch", headers={"Authorization": f"Bearer {AUTH_TOKEN}"}, json=data)
    if response.status_code == 200:
        colored_print("GPU instance started successfully.", Fore.GREEN)
    else:
        error_response = response.json()
        colored_print(f"Failed to start GPU instance. Error Code: {error_response['error']['code']}, Error Message: {error_response['error']['message']}", Fore.RED)


def stop_instance(instance_id):
    url = API_URL + "instance-operations/terminate"
    payload = {"instance_ids": [instance_id]}
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("\033[1;32mInstance terminated successfully.\033[0m")
    else:
        error_code = response.json()["error"]["code"]
        print(f"\033[1;31mFailed to terminate instance. Error Message: {error_code}\033[0m")


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
