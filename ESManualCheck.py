import sys
import os
import requests
import urllib.parse
import configparser
import subprocess
import shlex
import logging

logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()

def find_ini_file(start_path):
    current_path = start_path
    while current_path != os.path.dirname(current_path):
        ini_path = os.path.join(current_path, 'plugins', 'Manuals', 'config.ini')
        logging.info(f"Recherche config.ini sur : {ini_path}")
        if os.path.exists(ini_path):
            logging.info(f"Fichier config.ini trouvé : {ini_path}")
            return ini_path
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError("Le fichier config.ini n'a pas été trouvé.")

def load_config():
    global config
    config_ini_file_path = find_ini_file(os.getcwd())
    config.read(config_ini_file_path)

    base_path = os.path.dirname(os.path.dirname(os.path.dirname(config_ini_file_path)))
    logging.info(f"base_path: {base_path}")
    logging.info(f"config_ini_file_path: {config_ini_file_path}")

    for section in config.sections():
        for key in config[section]:
            logging.info(f"Key found: {key}")  # Ajout pour débogage
            if key.endswith('path'):
                relative_path = config[section][key]
                absolute_path = os.path.join(base_path, relative_path)
                config[section][key] = absolute_path
                logging.info(f"Path updated: {section}.{key} = {absolute_path}")
            else:
                logging.info(f"Non-path key: {section}.{key} = {config[section][key]}")

    return config

def execute_command(event, params):
    creation_flags = subprocess.CREATE_NO_WINDOW
    reader_path = config['Settings']['ReaderManualPath']
    command_template = config['Settings']['ReaderManualCommand']
    roms_path = config['Settings']['RomsPath']
    game = params.get('param2', '')
    logging.info(f"game: {game}")
    logging.info(f"param1: {params['param1']}")
    logging.info(f"roms_path: {roms_path}")
    system = params['param1'].replace(roms_path, '').split('\\')[0]
    logging.info(f"system: {system}")
    command = command_template.format(
        ReaderManualPath=reader_path,
        game=game,
        system=system
    )
    logging.info(f"Executing the command : {command}")
    #subprocess.Popen(command, shell=True, creationflags=creation_flags)
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flags)

def get_current_directory_event():
    return os.path.basename(os.getcwd())

def get_command_line():
    pid = os.getpid()
    command = f'wmic process where ProcessId={pid} get CommandLine'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if error:
        logging.info(f"Error: {error.decode('cp1252').strip()}")
        #input("Appuyez sur Entrée pour continuer...")
        return ""
    try:
        return output.decode('utf-8').strip()
    except UnicodeDecodeError:
        return output.decode('cp1252').strip()

def clean_and_split_arguments(command_line):
    command_line = command_line.replace('""', '"')
    try:
        arguments = shlex.split(command_line)
    except ValueError as e:
        logging.info(f"Erreur lors du découpage des arguments: {e}")
        arguments = []
    if arguments:
        arguments = arguments[2:]
    return arguments

if __name__ == "__main__":
    load_config()
    event = get_current_directory_event()
    command_line = get_command_line()
    logging.info(f"command_line: {command_line}")
    arguments = clean_and_split_arguments(command_line)
    params = {f'param{i}': arg for i, arg in enumerate(arguments, start=1)}
    logging.info(f"arguments: {arguments}")
    logging.info(f"params: {params}")
    #input("Appuyez sur Entrée pour continuer...")
    execute_command(event, params)
