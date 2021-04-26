import requests

url = ''
json = {
    'reporter': 'extreme4all',
    'reported': 'extreme4all',
    'region_id': 0,
    'x_coord': 0,
    'y_coord': 0,
    'z_coord': 0,
    'timestamp': 0,
    'manual_detect': 0,
    'on_members_world': 0
}
response = requests.get(url, json=json)
response.json()