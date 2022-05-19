import random
import sqlite3

global db
global sql

db = sqlite3.connect('Table with Russian cities.db')
sql = db.cursor()


class TheCityGame:
    def __init__(self):
        self.__Cities = {}
        self.__Alphabet = []
        self.__Answers = []

        for letter in sql.execute('SELECT * FROM russian_alphabet'):
            self.__Alphabet.append(letter[1])
            self.__Cities[letter[1]] = []

        for string in sql.execute('SELECT * FROM cities'):
            city = string[1]
            for key, value in self.__Cities.items():
                if city[0] == key:
                    value.append(city)

        self.__last_letter = ''
        self.__last_answer = ''
        self.__hints = 3
        self.__mistakes = 5
        self.__points = 0

    def __call__(self, msg):
        return self.game(msg)

    def game(self, msg):

        if msg == 'стоп':
            return self.end(1)

        if msg == 'буква':
            return f'Вам на "{self.__last_letter}".'

        if msg == 'подсказка':
            if self.__hints == 0:
                return "К сожалению, у вас нет больше подсказок."
            elif self.__last_letter == '':
                self.__last_answer = random.choice(random.choice((list(self.__Cities.values()))))
            else:
                self.__last_answer = random.choice(self.__Cities[self.__last_letter])
            self.__hints -= 1
            self.func_last_letter(self.__last_answer)
            self.__Cities[self.__last_answer[0]].remove(self.__last_answer)
            self.__Answers.append(self.__last_answer.lower())
            return self.__last_answer

        if msg in self.__Answers:
            return "Извините, но это город уже был. Напишите, пожалуйста, другой."

        if msg[0] != self.__last_letter.lower() and self.__last_letter != '':
            if self.__mistakes != 0:
                self.__mistakes -= 1
                return "Город не начинается с буквы, на которую закончился предыдущий!"
            else:
                return self.end(2)

        response_status = self.response_status(msg)
        if response_status[0]:
            list_of_possible_answers = []
            number = -1
            list_if_cities = []
            for values in self.__Cities.values():
                for city in values:
                    list_if_cities.append(city)

            while len(list_of_possible_answers) == 0:
                for city in list_if_cities:
                    if city[0].lower() == msg[number]:
                        list_of_possible_answers.append(city)
                number -= 1

            self.__points += 1
            self.__Cities[response_status[1][0]].remove(response_status[1])
            self.__Answers.append(msg.lower())

            random.shuffle(self.__Alphabet)
            for letter in self.__Alphabet:
                for possible_city in list_of_possible_answers:
                    if letter == possible_city[-1].upper():
                        self.__last_answer = possible_city
                        break

            self.__Answers.append(self.__last_answer.lower())
            self.__Cities[self.__last_answer[0].upper()].remove(self.__last_answer)
            self.func_last_letter(self.__last_answer)
            return self.__last_answer

        else:
            if self.__mistakes != 0:
                self.__mistakes -= 1
                return 'Этого города нет в моём списке.'
            else:
                return self.end(2)

    def response_status(self, msg):
        for city in self.__Cities[msg[0].upper()]:
            if msg == city.lower():
                return True, city
        return False, None

    def func_last_letter(self, copy_answer):
        number = -1
        while True:
            if self.__Cities[copy_answer[number].upper()]:
                self.__last_letter = copy_answer[number].upper()
                return
            number -= 1

    def end(self, position):
        points = self.__points
        if position == 1:
            return f'Игра окончена. Ваш счёт: {points}', False
        else:
            return f'К сожалению, у вас больше нет возможностей на ошибку. Игра окончена!\n' \
                   f'Ваш счёт: {points}', False
