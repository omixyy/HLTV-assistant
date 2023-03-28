from bs4 import BeautifulSoup
import requests
import sys
import ctypes
import time


class TeamComparer:
    def __init__(self):
        self.team_profile_link1, self.soup1 = None, None
        self.team_profile_link2, self.soup2 = None, None
        self.roster_stats1, self.roster_stats2 = dict(), dict()
        self.find_players = list()

    # Считывание статистики команды с hltv.org и вывод её на экран
    def get_team_stats(self, parse, tstv):
        self.find_players = parse.find_all("div", {"class": "players-cell playersBox-playernick text-ellipsis"})
        print(f'Team: {parse.find("h1", {"class": "profile-team-name text-ellipsis"}).text}')
        print(f'World ranking: '
              f'{parse.find_all("div", {"class": "profile-team-stat"})[0].text.strip("World ranking#")}')
        tstv['name'] = parse.find("h1", {"class": "profile-team-name text-ellipsis"}).text
        try:
            tstv['rank'] = int(list(
                parse.find_all("div", {"class": "profile-team-stat"})
            )[0].text.strip('World ranking#'))

        # Если у команды нет места в топе HLTV
        except ValueError:
            print('Not enough stats to complete analysis. Try again and rerun the program')
            time.sleep(10)
            sys.exit()

        try:
            print(f'Average player age: ' 
                  f'{float(parse.find_all("div", {"class": "profile-team-stat"})[2].text.strip("Average player age"))}')

        # Если нет необходимой информации
        except IndexError:
            print('Average player age: no info')

        # Если нет информации о среднем возрасте игроков
        except ValueError:
            print('Average player age: No info')
        print('\n\tRoster:')

        # Если есть тренер в команде, то не нужно учитывать его как игрока.
        # А если его нет, то чтобы не было ошибки, нужно учесть его место в HTML коде
        try:
            if len([i.text for i in self.find_players]) >= 6:
                print("  ".join([
                    self.find_players[player].text.strip('\n').rstrip('\n') for player in range(1, 6)
                ]))
            else:
                print("  ".join([
                    self.find_players[player].text.strip('\n').rstrip('\n') for player in range(0, 5)
                ]))

        # Если нет полной информации о составе команды
        except IndexError:
            print('Seems like there is not enough info about roster.\n'
                  'Please rerun the program and try again\n'
                  'Waiting 10 seconds before exiting')
            time.sleep(10)
            sys.exit()

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
        try:
            tstv['AR'] = (sum(stats_positive) + sum(stats_negative) + sum(stats_neutral)) /\
                         (len(stats_positive) + len(stats_negative) + len(stats_neutral))

        # Если нет полной статистики
        except ZeroDivisionError:
            print('Not enough stats to complete analysis.\n'
                  'Please rerun the program and try again\n'
                  'Waiting 10 seconds before leaving')
            time.sleep(10)
            sys.exit()
        matches = list()
        streak = 0

        # Составляем список из 1 и 0, где 1 - победный матч, 0 - проигранный
        for i in parse.find_all('div', {'class': 'score-cell'}):
            if i.text.split(':')[0] != '-' and int(i.text.split(':')[0]) > int(i.text.split(':')[1]):
                matches.append(1)
            if i.text.split(':')[0] != '-' and int(i.text.split(':')[0]) <= int(i.text.split(':')[1]):
                matches.append(0)

        # Подсчитываем победный стрик команды
        for i in matches:
            if i == 1:
                streak += 1
            if i == 0:
                break
        tstv['streak'] = streak

    # Метод, реализующий ввод никнеймов и получающий ссылки на профили игроков
    def input_team_names(self):
        ind1, ind2 = -1, -1
        name1 = input('Input first team name: -> ').lower()
        name2 = input('Input second team name: -> ').lower()
        response1 = requests.get('https://www.hltv.org/search?term=' + name1)
        response2 = requests.get('https://www.hltv.org/search?term=' + name2)
        soup1 = BeautifulSoup(response1.content, 'html.parser')
        soup2 = BeautifulSoup(response2.content, 'html.parser')
        for i in str(soup1).split(':'):
            ind1 += 1
            if "teams" in i:
                break
        for j in str(soup2).split(':'):
            ind2 += 1
            if "teams" in j:
                break
        ident1 = str(soup1).split(':')[ind1 + 2].rstrip(',"name')
        ident2 = str(soup2).split(':')[ind2 + 2].rstrip(',"name')
        self.team_profile_link1 = 'https://www.hltv.org/team/' + ident1 + '/' + name1
        self.team_profile_link2 = 'https://www.hltv.org/team/' + ident2 + '/' + name2
        self.get_response()

    # Ввод ссылок на профили команд
    def input_team_links(self):
        try:
            self.team_profile_link1 = input('Input first team profile link: -> ')
            self.team_profile_link2 = input('Input second team profile link: -> ')
            self.get_response()

        # Если введена не ссылка
        except requests.exceptions.MissingSchema:
            print('Found a line that is not a link!')
            print('Waiting 10 seconds before exiting.\nRerun the program')
            time.sleep(10)
            sys.exit()

    # Вызов функции получения статистики команд get_team_stats() и её вывода на экран
    def print_team_stats(self):
        try:
            self.get_team_stats(self.soup1, self.roster_stats1)
            print('\n     VS\n')
            self.get_team_stats(self.soup2, self.roster_stats2)

        # Если не удалось найти команду
        except AttributeError:
            print('Could not find this team.\nPlease try again and rerun the program')
            print('Waiting 10 seconds before exiting')
            time.sleep(10)
            sys.exit()

    # Метод, реализующий получение ответа от сервера
    def get_response(self):
        response1 = requests.get(self.team_profile_link1)
        response2 = requests.get(self.team_profile_link2)
        self.soup1 = BeautifulSoup(response1.content, 'html.parser')
        self.soup2 = BeautifulSoup(response2.content, 'html.parser')

    # Используя dll с кодом на C используется функция подсчёта вероятности и вывода её на экран
    def print_probability_t(self):
        cfile = ctypes.WinDLL('./probcount.dll')
        cfile.TeamStatsFormula.argtypes = [ctypes.c_int, ctypes.c_int,
                                           ctypes.c_float, ctypes.c_float,
                                           ctypes.c_int, ctypes.c_int]
        cfile.TeamStatsFormula.restype = ctypes.c_float
        print(f'\nAccording to my calculations '
              f'{self.roster_stats1["name"]} will defeat '
              f'{self.roster_stats2["name"]} with probability ',
              round(cfile.TeamStatsFormula(self.roster_stats1['rank'], self.roster_stats2['rank'],
                                           self.roster_stats1['AR'], self.roster_stats2['AR'],
                                           self.roster_stats1['streak'], self.roster_stats2['streak']), 1), '%')
