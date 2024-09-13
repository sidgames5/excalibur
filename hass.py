import requests

import config

access_token = config.hass_access_token
hass_url = config.hass_url

def getEntities():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(f"{hass_url}/api/states", headers=headers)
    
    if response.status_code == 200:
        all_entities = response.json()
        return all_entities
    else:
        print(f"Error: {response.status_code}")
        return None

def getEntitiesFromDomain(domain):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(f"{hass_url}/api/states", headers=headers)
    
    if response.status_code == 200:
        all_entities = response.json()
        domain_entities = [
            entity['entity_id'] 
            for entity in all_entities 
            if entity['entity_id'].startswith(f"{domain}.")
        ]
        return domain_entities
    else:
        print(f"Error: {response.status_code}")
        return None

def lightTurnOn(entity):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "entity_id": entity
    }
    
    url = f"{hass_url}/api/services/light/turn_on"
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error turning on light: {e}")
        return False

def lightTurnOff(entity):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "entity_id": entity
    }
    
    url = f"{hass_url}/api/services/light/turn_off"
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error turning off light: {e}")
        return False
    
def sceneActivate(entity):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "entity_id": entity
    }
    
    url = f"{hass_url}/api/services/scene/turn_on"
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error activating scene: {e}")
        return False