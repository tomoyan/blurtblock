import pyrebase
import base64
import json
import os
from datetime import datetime
import requests

# Firebase configuration
serviceAccountCredentials = json.loads(
    base64.b64decode(os.environ.get('FB_SERVICEACCOUNT').encode()).decode())

firebase_config_prd = {
    "apiKey": os.environ.get('FB_APIKEY'),
    "authDomain": os.environ.get('FB_AUTHDOMAIN'),
    "databaseURL": os.environ.get('FB_DATABASEURL'),
    "storageBucket": os.environ.get('FB_STORAGEBUCKET'),
    "serviceAccount": serviceAccountCredentials,
}
firebase = pyrebase.initialize_app(firebase_config_prd)

# Get a reference to the database service
db_prd = firebase.database()
db_name = 'coal_list'


def main():
    print('UPDATE_COAL_START')

    import_coal_file()

    print('UPDATE_COAL_END')


def is_coal(username=''):
    result = False

    if not username:
        return

    coal = db_prd.child(
        db_name).order_by_child("username").equal_to(username).get().val()

    if len(coal):
        result = True

    print('IS_COAL:', username, result)
    return result


def add_to_coal_list(username=''):
    print("ADD_TO_COAL_LIST", username)
    # add username to a coal_list

    now = datetime.utcnow()
    current_time = now.strftime("%m/%d/%Y %H:%M:%S")

    data = {
        "username": username,
        "created": current_time,
    }

    result = db_prd.child(db_name).push(data)
    print("SAVE_RESULT ", result)


def import_coal_file():
    print('IMPORT_COAL_FILE')

    # access coal raw file
    base_url = 'https://gitlab.com'
    url = (
        f'{base_url}'
        '/blurt/openblurt/coal/-/raw/master/coal.json'
    )

    response = requests.get(url)
    coal_json = response.json()

    for username in coal_json:
        # skip if username exists in fb
        if is_coal(username):
            continue

        add_to_coal_list(username)


if __name__ == '__main__':
    main()
