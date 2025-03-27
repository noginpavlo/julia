import requests
import sqlite3


def get_definition(input_word):
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}'
    response = requests.get(url)
    with sqlite3.connect("db.sqlite") as connect:
        cursor = connect.cursor()
        cursor.execute(
            '''
                    SELECT COUNT (*) FROM vocabulary WHERE word = ?
                ''', (input_word.upper(),)
        )
        result = cursor.fetchone()

def create_database():
    with sqlite3.connect("db.sqlite3") as connect:
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


create_database()
# get_definition("cat")