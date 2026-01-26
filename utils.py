import json
import os

def interpolate(template, input):
    try:
        return template.format(**input)
    except KeyError:
        pass
    return template

def sanitize_cpf():
    return

def file_path(file_path):
    return f"{os.getcwd()}\\{file_path}"

def get_template(file_path):
    with open(file_path, "r") as f:
        return json.load(f)