import fitz  # PyMuPDF
import pygame
import sys
import os
import configparser
import logging

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()

import xml.etree.ElementTree as ET

def load_input_config():
    # Obtenir le chemin du répertoire courant
    current_dir = os.getcwd()

    # Remonter de deux niveaux dans l'arborescence des dossiers
    # version appelé du script
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    # version dev dans dossier plugins/Manuals/
    #current_dir = os.path.dirname(os.path.dirname(current_dir))

    # Construire le chemin vers es_input.cfg
    path_to_es_input = os.path.join(current_dir, 'emulationstation', '.emulationstation', 'es_input.cfg')

    tree = ET.parse(path_to_es_input)
    root = tree.getroot()

    key_ids = {'pagedown': [], 'pageup': [], 'hotkey': []}

    devices_key_ids = {}

    for inputConfig in root.findall('inputConfig'):
        device_type = inputConfig.get('type')
        device_name = inputConfig.get('deviceName')
        device_guid = inputConfig.get('deviceGUID')

        key_ids = {'pagedown': [], 'pageup': [], 'hotkey': []}
        for inputEntry in inputConfig.findall('input'):
            name = inputEntry.get('name')
            id = inputEntry.get('id')
            if name in key_ids:
                key_ids[name].append(int(id))

        devices_key_ids[(device_type, device_name, device_guid)] = key_ids

    return devices_key_ids

def save_current_page(game, current_page, current_working_dir):
    manuals_dir = os.path.join(current_working_dir)
    if not os.path.exists(manuals_dir):
        os.makedirs(manuals_dir)

    pin_file_path = os.path.join(manuals_dir, f"{game}.pin")
    with open(pin_file_path, 'w') as file:
        file.write(str(current_page))

def load_last_page(game, current_working_dir):
    pin_file_path = os.path.join(current_working_dir, f"{game}.pin")
    if os.path.exists(pin_file_path):
        with open(pin_file_path, 'r') as file:
            return int(file.read().strip())
    return 0  # Retourne 0 si le fichier n'existe pas

def extract_game_and_system(args):
    game = next((arg.split("=")[1] for arg in args if "--game" in arg), "")
    system = next((arg.split("=")[1] for arg in args if "--system" in arg), "")
    return game, system

def get_pdf_path(system, game):
    # Obtention du répertoire de travail actuel
    current_dir = os.getcwd()
    # version appelé du script
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    # version dev dans dossier plugins/Manuals/
    #current_dir = os.path.dirname(os.path.dirname(current_dir))

    # Construction du chemin vers le pdf du manual
    manual_path = os.path.join(current_dir, 'roms', system, 'manuals', f"{game}-manual.pdf")

    # Vérification de l'existence du fichier pdf
    if not os.path.exists(manual_path):
        logging.info(f"Fichier {manual_path}  non trouvé pour {system}/{game}")
        sys.exit(1)
        # Si non trouvé, utilisation du chemin du fichier INI par défaut
        #ini_path = os.path.join(current_working_dir, 'mappers', 'default.ini')

    # Affichage du chemin du fichier INI pour le débogage
    print(f"Chemin du fichier PDF: {manual_path}")
    return manual_path

def show_pdf_fullscreen(pdf_path, game, system, joystick_keys, joystick):
    # Obtention du répertoire de travail actuel
    current_dir = os.getcwd()
    # version appelé du script
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    # version dev dans dossier plugins/Manuals/
    #current_dir = os.path.dirname(os.path.dirname(current_dir))

    current_dir = os.path.join(current_dir, 'plugins', 'Manuals', 'manuals', system)

    infoObject = pygame.display.Info()
    screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
    doc = fitz.open(pdf_path)
    current_page = load_last_page(game, current_dir)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                hotkey_id = joystick_keys.get('hotkey', [None])[0]
                pagedown_id = joystick_keys.get('pagedown', [None])[0]
                pageup_id = joystick_keys.get('pageup', [None])[0]

                if joystick.get_button(hotkey_id):
                    save_current_page(game, current_page, current_dir)
                    running = False
                elif joystick.get_button(pagedown_id):
                    current_page = min(current_page + 1, doc.page_count - 1)
                elif joystick.get_button(pageup_id):
                    current_page = max(current_page - 1, 0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_current_page(game, current_page, current_dir)
                    running = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                    current_page = min(current_page + 1, doc.page_count - 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    current_page = max(current_page - 1, 0)

        # Code pour afficher la page actuelle du PDF et la centrer
        page = doc.load_page(current_page)
        zoom_x = infoObject.current_w / page.rect.width
        zoom_y = infoObject.current_h / page.rect.height
        zoom = min(zoom_x, zoom_y)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Calcul des marges pour centrer l'image
        margin_x = (infoObject.current_w - pix.width) // 2
        margin_y = (infoObject.current_h - pix.height) // 2

        img = pygame.image.fromstring(pix.samples, (pix.width, pix.height), "RGB")

        # Remplir l'écran avec du noir
        screen.fill((0, 0, 0))

        # Blit l'image au centre de l'écran
        screen.blit(img, (margin_x, margin_y))
        pygame.display.flip()

    doc.close()

import time  # Importez time pour utiliser la fonction sleep
def main_loop():
    devices_key_ids = load_input_config()
    print(devices_key_ids)

    game, system = extract_game_and_system(sys.argv)
    if not game or not system:
        print("Erreur : Paramètres 'game' et 'system' manquants.")
        sys.exit(1)
    pdf_path = get_pdf_path(system, game)

    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    print(f"Nombre de joysticks détectés: {len(joysticks)}")
    for joystick in joysticks:
        joystick.init()
        print(f"Joystick initialisé : {joystick.get_name()}, GUID : {joystick.get_guid()}")
    # État des touches pour chaque joystick
    joystick_states = {joystick.get_instance_id(): {} for joystick in joysticks}

    def cleanGuid(guid):
        return guid[:4] + '0000' + guid[8:]

    def get_device_keys(guid, devices_key_ids):
        for (device_type, device_name, device_guid), keys in devices_key_ids.items():
            if device_type == "joystick" and device_guid == guid:
                return keys
        return {}

    while True:
        for event in pygame.event.get():
            if event.type in [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
                instance_id = event.instance_id
                button_pressed = event.type == pygame.JOYBUTTONDOWN

                for joystick in joysticks:
                    if joystick.get_instance_id() == instance_id:
                        print(f"devices_key_ids : {devices_key_ids}")
                        guid = cleanGuid(joystick.get_guid())
                        print(f"clean joystick.get_guid() : {guid}")
                        joystick_keys = get_device_keys(guid, devices_key_ids)
                        print(f"joystick_keys : {joystick_keys}")

                        # Mettre à jour l'état de la touche
                        joystick_states[instance_id][event.button] = button_pressed

                        # Obtenir l'ID du bouton hotkey et pagedown pour ce joystick
                        hotkey_id = joystick_keys.get('hotkey', [None])[0]
                        pagedown_id = joystick_keys.get('pagedown', [None])[0]
                        print(f"hotkey_id : {hotkey_id}")
                        print(f"pagedown_id : {pagedown_id}")
                        print(f"event.button : {event.button}")

                        # Vérifier si le bouton hotkey et le bouton pagedown sont pressés
                        hotkey_pressed = joystick_states[instance_id].get(hotkey_id, False)
                        pagedown_pressed = joystick_states[instance_id].get(pagedown_id, False)

                        print(f"Joystick bouton {event.button} {'pressé' if button_pressed else 'relâché'}, GUID: {guid}, Instance ID: {instance_id}, Hotkey pressé: {hotkey_pressed}, Pagedown pressé: {pagedown_pressed}")

                        if hotkey_pressed and pagedown_pressed:
                            show_pdf_fullscreen(pdf_path, game, system, joystick_keys, joystick)
                            print(f"show_pdf_fullscreen quit")
                            pygame.display.quit()
                            pygame.quit()
                            time.sleep(1)
                            pygame.init()
                            pygame.joystick.init()
                            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
                            print(f"Nombre de joysticks détectés: {len(joysticks)}")
                            for joystick in joysticks:
                                joystick.init()
                                print(f"Joystick initialisé : {joystick.get_name()}, GUID : {joystick.get_guid()}")
                            # État des touches pour chaque joystick
                            joystick_states = {joystick.get_instance_id(): {} for joystick in joysticks}
                            break

    print(f"pygame quit")
    pygame.display.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()
