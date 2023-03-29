from bs4 import BeautifulSoup
import grequests
import requests
import ctypes
import os


class Events:
    def __init__(self):
        self.all_events_link = 'https://www.hltv.org/events'
        self.event_to_parse_link = 'https://www.hltv.org'
        self.event_link = str()
        self.events_to_links = dict()
        self.counter_to_event = dict()
        self.teams_to_links = dict()
        self.all_team_stats = list()
        self.matches = list()
        self.streak, self.counter = 0, 1
        self.event = str()

    # Метод, реализующий получение всех предстоящих ивентов
    def get_events(self):
        response = requests.get(self.all_events_link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Поиск ивентов
        for i in soup.find('div', {'class': 'events-month'}).find_all('a'):
            line = i.text.replace('\n', ' ').rstrip('   Date Prize Teams     ').split('       ')
            if line[0][5] != ' ':
                self.events_to_links[line[0].split('  ')[2]] = self.event_to_parse_link + i.get('href')
            else:
                self.events_to_links[line[0].split('  ')[3]] = self.event_to_parse_link + i.get('href')

    # Метод, выводящий все ивенты на экран
    def print_events(self):
        for event, link in self.events_to_links.items():
            print(f'{self.counter} - {event}')
            self.counter_to_event[self.counter] = event
            self.counter += 1

    # Ввод номера ивента
    def input_event(self):
        event_num = input('Input the number of event -> ')
        while event_num not in list(map(lambda x: str(x), range(1, self.counter))):
            event_num = input('No such event!\nPlease input the number of event again: ')
        self.event = self.counter_to_event[int(event_num)]
        self.event_link = self.events_to_links[self.event]
        self.counter = 1

    # Метод, реализующий получение статистики команд
    def get_stats(self, parse, tstv):
        # print(parse.find("h1", {"class": "profile-team-name text-ellipsis"}))
        tstv['name'] = parse.find("h1", {"class": "profile-team-name text-ellipsis"}).text
        tstv['rank'] = int(list(
            parse.find_all("div", {"class": "profile-team-stat"})
        )[0].text.strip('World ranking#'))

        # Считывание информации о рейтингах игроков
        stats_negative = [float(i.text) for i in
                          parse.find_all(
                              'div', {'class': 'players-cell rating-cell ratingNegative'}
                          )]
        stats_positive = [float(i.text) for i in
                          parse.find_all(
                              'div', {'class': 'players-cell rating-cell ratingPositive'}
                          )]
        stats_neutral = [float(i.text) for i in
                         parse.find_all(
                             'div', {'class': 'players-cell rating-cell ratingNeutral'}
                         )]

        # Создание среднего рейтинга игроков команды
        tstv['AR'] = (sum(stats_positive) + sum(stats_negative) + sum(stats_neutral)) / \
                     (len(stats_positive) + len(stats_negative) + len(stats_neutral))

        # Составляем список из 1 и 0, где 1 - победный матч, 0 - проигранный
        for i in parse.find_all('div', {'class': 'score-cell'}):
            if i.text.split(':')[0] != '-' and int(i.text.split(':')[0]) > int(i.text.split(':')[1]):
                self.matches.append(1)
            if i.text.split(':')[0] != '-' and int(i.text.split(':')[0]) <= int(i.text.split(':')[1]):
                self.matches.append(0)

        # Подсчитываем победный стрик команды
        for i in self.matches:
            if i == 1:
                self.streak += 1
            if i == 0:
                break
        tstv['streak'] = self.streak
        self.streak = 0
        self.matches = list()

    # Вывод информации об ивенте
    def print_event_info(self):
        tstv = dict()
        response = requests.get(self.event_link)
        soup = BeautifulSoup(response.content, 'html.parser')
        print('\nParticipating teams:')

        try:
            for i in soup.find('div', {'class': 'teams-attending grid'}).find_all('div', {'class': 'team-name'}):
                team_name = i.find('div', {'class': 'text-container'}).text.strip('\n').rstrip('\n')
                print(team_name)
                self.teams_to_links[team_name] = 'https://www.hltv.org' + i.find('a').get('href')

        # Если нет полноценной информации об участвующих командах
        except AttributeError:
            print('No info')

        print(f"Total prize pool: {soup.find('td', {'class': 'prizepool text-ellipsis'}).text}")
        print(f'Date: {soup.find("td", {"class": "eventdate"}).text}')
        print('Analysing is in progress, please wait...')

        # Получение статистики каждой участвующей команды ![БЫЛО долго]
        # С использованием grequests удалось сократить время работы программы примерно на 5-6 секунд
        matches_links = [v for k, v in self.teams_to_links.items()]
        all_responses = (grequests.get(url) for url in matches_links)
        mapped_responses = grequests.map(all_responses)
        for resp in mapped_responses:
            soup = BeautifulSoup(resp.content, 'html.parser')
            self.get_stats(soup, tstv)
            self.all_team_stats.append(tstv)
            tstv = {}

    # Вывод предположительных вероятностей побед команд
    def print_probability_e(self):
        os.system('cls')

        # Указание на то, какие типы принимают и возвращают функции на Си
        cfile = ctypes.WinDLL('./custom_libs/probcount.dll')
        cfile.CountTeamStrength.argtypes = [ctypes.c_int, ctypes.c_float, ctypes.c_int]
        cfile.EventFormula.argtypes = [ctypes.c_float] * 2
        cfile.CountTeamStrength.restype = ctypes.c_float
        cfile.EventFormula.restype = ctypes.c_float
        team_name_to_strength = dict()

        print(f'According to my calculations,\neach team can win {self.event} with probability:\n')

        # Вывод названия команды и вероятности её победы на турнире
        for team_info in self.all_team_stats:
            for key, val in team_info.items():
                if key == 'name':
                    team_name_to_strength[val] = cfile.CountTeamStrength(team_info['rank'],
                                                                         team_info['AR'],
                                                                         team_info['streak'])

        # Подсчёт суммарной "силы" команд, после чего на её основе производится расчёт вероятности
        summary = sum(map(lambda x: float(x), team_name_to_strength.values()))
        for key, val in team_name_to_strength.items():
            print(f'{key} - {round(cfile.EventFormula(float(val), summary), 1)} %')
