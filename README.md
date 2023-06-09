# Lambda Script
Command line app to interact with Lambda Labs GPUs

# Installation
```
git clone https://github.com/cybrly/LambdaScript.git
cd LambdaScript
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Usage
```
python3 lambda.py -h                                                                                                                                 ─╯

    USAGE:
        python script_name.py [COMMAND] [ARGUMENT]

    COMMANDS:
        check               Check the status of running instances.
        start <number>      Start a GPU instance with the given number.
        stop <instance_id>  Terminate the instance with the given instance id.
        list                List all available GPU instances.
```
