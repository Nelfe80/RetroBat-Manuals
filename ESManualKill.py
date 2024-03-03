import os
import configparser
import subprocess
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)

def find_ini_file(start_path):
    current_path = start_path
    while current_path != os.path.dirname(current_path):
        ini_path = os.path.join(current_path, 'plugins', 'Manuals', 'config.ini')
        if os.path.exists(ini_path):
            return ini_path
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError("Le fichier config.ini n'a pas été trouvé.")

def load_config():
    current_working_dir = os.getcwd()
    config_path = find_ini_file(current_working_dir)
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def execute_kill_command(config):
    kill_command = config['Settings']['ReaderManualKillCommand']
    logging.info(f"Executing kill command: {kill_command}")
    process = subprocess.run(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    try:
        config = load_config()
        execute_kill_command(config)
    except Exception as e:
        logging.error(f"An error occurred: {e}")