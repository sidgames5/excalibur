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

def getDomains():
    return