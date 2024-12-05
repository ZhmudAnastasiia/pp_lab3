
import requests
import json

class NetworkHelper:
    def getlist(url):
        response = requests.get(url)
        print(f'ping status code: {response.status_code}')
        print(f'ping body: {response.text}')
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                print("Error parsing JSON:", e)
            return []  
        else:
            return [] 

    def getbyID(url):
        response = requests.get(url)
        print(f'ping status code: {response.status_code}')
        print(f'ping body: {response.text}')
        return response.json()

    def create(url, data):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        response_json = response.json()
        print(f'ping status code: {response.status_code}')
        print(f'response json: {type(response_json)} {response_json}')
        print(f'ping body: {response.text}')
        return response_json

    def delete(url):
        response = requests.delete(url)
        print(f'ping status code: {response.status_code}')

    def update(url, data):
        headers = {'Content-Type': 'application/json'}
        response = requests.put(url=url, headers=headers, data=json.dumps(data))
        print(f'ping status code: {response.status_code}')
        print(f'ping body: {response.text}')
