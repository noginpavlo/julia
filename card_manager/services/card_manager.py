import requests
from datetime import date
import sqlite3
import random

today_date = str(date.today())

def get_word(input_word):
    global today_date
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}'
    response = requests.get(url)
    print(f"This is RESPONSE: {response}")
    with sqlite3.connect("sqlite3.db") as connect:
        cursor = connect.cursor()
        cursor.execute(
            '''
                    SELECT COUNT (*) FROM vocabulary WHERE word = ?
                ''', (input_word.upper(),)
        )
        result = cursor.fetchone()
        print(f"This is 'result 0': {result[0]}")
        if result[0] > 0:
            return "Word already in dictionary"
        elif response.status_code == 200:
            response = response.json()
            word = input_word.upper()
            record_date = today_date
            phonetics = response[0].get('phonetic', "not found")
            definition = response[0]['meanings'][0]['definitions'][0].get('definition', "No definition found")
            example = response[0]['meanings'][0]['definitions'][0].get('example', "No example found")

            array = (record_date, word, phonetics, definition, example, 1)
            if len(array) == 6:
                with sqlite3.connect("sqlite3.db") as connection:
                    cursor = connection.cursor()
                    cursor.execute('''
                                       INSERT INTO vocabulary (date, word, phonetics, definition, example, increment)
                                       VALUES (?, ?, ?, ?, ?, ?);
                                   ''', (array[0], array[1], array[2], array[3], array[4], array[5]))
                return "Success"
            else:
                # add some meaningful error here
                return "Some error occurred that I need to clasify later"
        else:
            return "Unable to find"


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

def pull_random_card():
    with sqlite3.connect("sqlite3.db") as connect:
        cursor = connect.cursor()
        cursor.execute('''
                        SELECT id FROM vocabulary WHERE date <= ?
                    ''', (date.today(), ))
        result = cursor.fetchall()

        if not result:
            raise ValueError("No cards available for the given date.")

        random_word_id = random.choice(result)[0]
    return random_word_id


def make_card(card_id):
    with sqlite3.connect("sqlite3.db") as connect:
        cursor = connect.cursor()
        cursor.execute('''
                    SELECT * FROM vocabulary WHERE id = ? AND date <= ?
                        ''', (card_id, date.today()))
        row = cursor.fetchall()

        word_title = row[0][2]
        word_phonetics = row[0][3]
        word_definition = row[0][4]
        word_example = row[0][5]
    print(
        f"Here is a RANDOM card that will appear on the frontend:\nWord title: {word_title},\n"
        f"Word phonetics :{word_phonetics},\nWord definition: {word_definition},\nWord example: {word_example}"
    )
    return word_title, word_phonetics, word_definition, word_example



information = get_word("order")
print(f"This is what get_data() returns: {information}")
word_id = pull_random_card()
make_card(word_id)
