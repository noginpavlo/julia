"""This is a test file for manual testing dictionaryapi.dev"""
import requests


url = "https://api.dictionaryapi.dev/api/v2/entries/en/cat"
response = requests.get(url)

print(response.status_code)
print(response.json())
