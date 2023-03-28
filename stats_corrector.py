from bs4 import BeautifulSoup
import requests
import sys
import ctypes
import time


class Corrector:
    def __init__(self):
        self.soup = None
        self.stats = {'1': '0',
                      '2': '1',
                      '3': '2',
                      '4': '4'}
        self.stc, self.name = dict(), str()
        self.new_stat, self.play_stat = float(), float()

    # Метод, в котором реализован ввод ссылки на профиль игрока и получение ответа от сайта
    def input_profile_link(self):
        try:
            link = input('Input player profile link: -> ')
            self.name = link.split('/')[-1]
            response = requests.get(link)
            self.soup = BeautifulSoup(response.content, 'html.parser')

        # Если была введена не ссылка
        except requests.exceptions.MissingSchema:
            print('Found a line that is not a link!')
            print('Waiting 10 seconds before exiting')
            time.sleep(10)
            sys.exit()

    # Метод, в котором реализован ввод никнейма игрока и получение ответа от сайта
    def input_player_nickname(self):
        nickname = input('Input player nickname: -> ').lower()
        resp = requests.get('https://www.hltv.org/search?term=' + nickname)
        soup = BeautifulSoup(resp.content, 'html.parser')
        ident = str(soup).split(':')[2].rstrip(',"nickName"')
        link = 'https://www.hltv.org/player/' + ident + '/' + nickname
        self.soup = BeautifulSoup(requests.get(link).content, 'html.parser')
        self.name = link.split('/')[-1]

    # Метод, реализующий ввод необходимых данных для осуществления анализа
    def get_stat(self):
        stat = input('Which stat do you want to correct?\n'
                     '1) Rating 2.0   2) KPR   3) HS   4) DPR\n-> ')
        self.new_stat = float(input('Which value do you want to get? -> '))
        self.play_stat = float(input('With which stat are you going to play? -> '))
        while stat not in self.stats:
            stat = input('Could not find this option. Try again: ')
        stat = self.stats[stat]
        try:
            self.stc = float([i.find("p").text.rstrip("%")
                              for i in self.soup.find_all('div', {'class': 'player-stat'})][int(stat)])

        # Если не удалось найти профиль игрока или у него недостаточно статистики в профиле
        except IndexError:
            print('Something went wrong.\nPlease rerun the program and try again')
            time.sleep(10)
            sys.exit()

    # Метод, пропечатывающий итоговый результат, полученный из dll
    def correct(self):
        cfile = ctypes.WinDLL('./probcount.dll')
        cfile.StatsCorrector.argtypes = [ctypes.c_float, ctypes.c_float,
                                         ctypes.c_float, ctypes.c_int]
        cfile.StatsCorrector.restype = ctypes.c_int
        all_stats = [i.find("p").text for i in self.soup.find_all('div', {'class': 'player-stat'})]
        print(f'Player {self.name} needs', cfile.StatsCorrector(self.stc, self.new_stat,
                                                                self.play_stat, int(all_stats[3])), 'matches')
