import requests
from datetime import date
import sqlite3

today_date = str(date.today())

def get_definition(input_word):
    global today_date
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}'
    response = requests.get(url)
    with sqlite3.connect("sqlite3.db") as connect:
        cursor = connect.cursor()
        cursor.execute(
            '''
                    SELECT COUNT (*) FROM vocabulary WHERE word = ?
                ''', (input_word.upper(),)
        )
        result = cursor.fetchone()
        print(result[0])
        if result[0] > 0:
            return "Word already in dictionary"
        elif response.status_code == 200:
            response = response.json()
            word = input_word.upper()
            record_date = today_date
            try:
                phonetics = response[0]['phonetic']
            except KeyError:
                phonetics = "not found"
            definition = response[0]['meanings'][0]['definitions'][0]['definition']
            try:
                example = response[0]['meanings'][0]['definitions'][0]['example']
            except KeyError:
                example = "No example found."
            increment = 1
            print(record_date, word, phonetics, definition, example, increment)
            return record_date, word, phonetics, definition, example, increment
        else:
            return "Unable to find"


def save_word(array):
    if len(array) == 6:
        with sqlite3.connect("sqlite3.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                               INSERT INTO vocabulary (date, word, phonetics, definition, example, increment)
                               VALUES (?, ?, ?, ?, ?, ?);
                           ''', (array[0], array[1], array[2], array[3], array[4], array[5]))
    else:
        print(array)

def create_database():
    with sqlite3.connect("sqlite3.db") as connect:
        cursor = connect.cursor()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS vocabulary
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        word TEXT,
                        phonetics TEXT,
                        definition TEXT,
                        example TEXT,
                        increment INT
                        )
                    ''')


information = get_definition("cat")
save_word(information)