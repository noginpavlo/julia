# import requests
# from datetime import date
# import sqlite3
# import random
#
# today_date = str(date.today())
#
#
# def catch_errors(func):
#     def wrapper(*args):
#         try:
#             return func(*args)
#         except Exception as e:
#             raise e
#     return wrapper
#
#
# @catch_errors
# def get_data(input_word):
#     global today_date
#     url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}'
#     response = requests.get(url)
#
#     # This word does not exist error
#     if response.status_code == 404:
#         raise ValueError(f"Data not available for the word: {input_word} (404 Error)")  # Raise custom error
#
#     # Catching any kind of other errors related to api data retrieving
#     if response.status_code != 200:
#         raise ValueError(f"Unexpected error occurred with status code: {response.status_code}")
#
#     return response, input_word
#
#
# @catch_errors
# def process_data(response, input_word):
#
#     # Checking if the word is already in db
#     with sqlite3.connect("sqlite3.db") as connect:
#         cursor = connect.cursor()
#         cursor.execute(
#             '''
#                     SELECT COUNT (*) FROM vocabulary WHERE word = ?
#                 ''', (input_word.upper(),)
#         )
#         result = cursor.fetchone()
#
#         # Word already in the dictionary error
#         if result[0] > 0:
#             raise IndexError("Word already in the dictionary")
#
#         response = response.json()
#         record_date = today_date
#         phonetics = response[0].get('phonetic', "not found")
#         definition = response[0]['meanings'][0]['definitions'][0].get('definition', "No definition found")
#         example = response[0]['meanings'][0]['definitions'][0].get('example', "No example found")
#
#         return record_date, input_word.upper(), phonetics, definition, example, 1
#
#
# @catch_errors
# def save_data(array):
#     if len(array) == 6:
#         with sqlite3.connect("sqlite3.db") as connection:
#             cursor = connection.cursor()
#             cursor.execute('''
#                                INSERT INTO vocabulary (date, word, phonetics, definition, example, increment)
#                                VALUES (?, ?, ?, ?, ?, ?);
#                            ''', (array[0], array[1], array[2], array[3], array[4], array[5]))
#         print(f"Successfully recorder data on '{array[1]}' word")
#         return "Success"
#
#
# def create_database():
#     with sqlite3.connect("sqlite3.db") as connect:
#         cursor = connect.cursor()
#         cursor.execute('''
#                         CREATE TABLE IF NOT EXISTS vocabulary
#                         (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         date TEXT,
#                         word TEXT,
#                         phonetics TEXT,
#                         definition TEXT,
#                         example TEXT,
#                         increment INT
#                         )
#                     ''')
#
#
# @catch_errors
# def pull_random_card():
#     with sqlite3.connect("sqlite3.db") as connect:
#         cursor = connect.cursor()
#         cursor.execute('''
#                         SELECT id FROM vocabulary WHERE date <= ?
#                     ''', (date.today(), ))
#         result = cursor.fetchall()
#
#         # No words to choose from error
#         if not result:
#             raise ValueError("No cards available for the given date.")
#
#         random_word_id = random.choice(result)[0]
#     return random_word_id
#
#
# def make_card(card_id):
#     with sqlite3.connect("sqlite3.db") as connect:
#         cursor = connect.cursor()
#         cursor.execute('''
#                     SELECT * FROM vocabulary WHERE id = ? AND date <= ?
#                         ''', (card_id, date.today()))
#         row = cursor.fetchall()
#
#         word_title = row[0][2]
#         word_phonetics = row[0][3]
#         word_definition = row[0][4]
#         word_example = row[0][5]
#     print(
#         f"Here is a RANDOM card that will appear on the frontend:\nWord title: {word_title},\n"
#         f"Word phonetics :{word_phonetics},\nWord definition: {word_definition},\nWord example: {word_example}"
#     )
#     return word_title, word_phonetics, word_definition, word_example
#
#
# def main(user_input):
#     try:
#         information, word = get_data(user_input)
#         processed_data = process_data(information, word)
#         save_data(processed_data)
#
#     except Exception as e:
#         print(f"Execution stopped due to error: {str(e)}")
#
#
# word_id = pull_random_card()
# make_card(word_id)
#
#
# if __name__ == "__main__":
#     main("kind")
