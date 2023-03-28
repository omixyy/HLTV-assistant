from bs4 import BeautifulSoup
import requests
import sys
import ctypes
import time


class PlayerComparer:
    def __init__(self):
        self.stats_to_values1, self.stats_to_values2 = dict(), dict()
        self.player_profile_link1, self.player_profile_link2 = str(), str()
        self.player_found = False
        self.stats, self.stv = dict(), dict()
        self.soup1, self.soup2 = None, None
        self.nickname1, self.nickname2 = str(), str()
        self.cfile = ctypes.WinDLL('./probcount.dll')

    # Считывание статистики игрока с hltv.org и вывод её на экран по ссылке
    def get_player_stats(self, parse, stv):
        nickname = parse.find("div", {"class": "playerName"}).find("h1").string
        print(f'Player: {nickname}')
        stv['nick'] = nickname
        self.player_found = True
        print(f'Name:{parse.find("div", {"class": "playerRealname"}).text}')
        print(f'Country: {parse.find("div", {"class": "playerRealname"}).find("img").get("alt")}')
        print(f'Age: {parse.find("span", {"class": "listRight"}).text}')
        print(f'Team: {parse.find("span", {"class": "listRight text-ellipsis"}).find("img").get("alt")}')
        self.stats = parse.find_all('p')
        rating = str(self.stats[0]).strip("<p>").rstrip("</p>")
        kpr = str(self.stats[1]).strip("<p>").rstrip("</p>")
        dpr = str(self.stats[4]).strip("<p>").rstrip("</p>")
        hs = str(self.stats[2]).strip("<p>").rstrip("</p>").rstrip('%')
        print(f'Rating 2.0: {rating}')
        stv['rt'] = float(rating)
        print(f'Kills per round: {kpr}')
        stv['kpr'] = float(kpr)
        print(f'Deaths per round: {dpr}')
        stv['dpr'] = float(dpr)
        print(f'Headshots: {hs} %')
        stv['hs'] = float(hs)

    # Ввод ссылок на профили игроков
    def input_player_links(self):
        try:
            self.player_profile_link1 = input('Input first player profile link: -> ')
            self.player_profile_link2 = input('Input second player profile link: -> ')
            response1 = requests.get(self.player_profile_link1)
            response2 = requests.get(self.player_profile_link2)
            self.soup1 = BeautifulSoup(response1.content, 'html.parser')
            self.soup2 = BeautifulSoup(response2.content, 'html.parser')

        # Если была введена не ссылка
        except requests.exceptions.MissingSchema:
            print('Found a line that is not a link!')
            print('Waiting 10 seconds before exiting')
            time.sleep(10)
            sys.exit()

    # Ввод по никнейму
    def input_nicknames(self):
        try:
            self.nickname1 = input('Input first player nickname: -> ').lower()
            self.nickname2 = input('Input second player nickname: -> ').lower()
            response1 = requests.get('https://www.hltv.org/search?term=' + self.nickname1)
            response2 = requests.get('https://www.hltv.org/search?term=' + self.nickname2)
            soup1 = BeautifulSoup(response1.content, 'html.parser')
            soup2 = BeautifulSoup(response2.content, 'html.parser')
            ident1 = str(soup1).split(':')[2].rstrip(',"nickName"')
            ident2 = str(soup2).split(':')[2].rstrip(',"nickName"')
            self.player_profile_link1 = 'https://www.hltv.org/player/' + ident1 + '/' + self.nickname1
            self.player_profile_link2 = 'https://www.hltv.org/player/' + ident2 + '/' + self.nickname2
            self.soup1 = BeautifulSoup(requests.get(self.player_profile_link1).content, 'html.parser')
            self.soup2 = BeautifulSoup(requests.get(self.player_profile_link2).content, 'html.parser')

        # Если была введена не ссылка
        except requests.exceptions.MissingSchema:
            print('Found a line that is not a link!')
            print('Waiting 10 seconds before exiting')
            time.sleep(10)
            sys.exit()

    # Вызов функции вывода статистики игрока get_player_stats()
    def print_player_stats(self):
        self.cfile.DrawDiagram.argtypes = [ctypes.c_float] * 4
        try:
            self.get_player_stats(self.soup1, self.stats_to_values1)
            self.cfile.DrawDiagram(self.stats_to_values1['rt'], self.stats_to_values1['kpr'],
                                   self.stats_to_values1['dpr'], self.stats_to_values1['hs'])
            print('\n      VS\n')
            self.get_player_stats(self.soup2, self.stats_to_values2)
            self.cfile.DrawDiagram(self.stats_to_values2['rt'], self.stats_to_values2['kpr'],
                                   self.stats_to_values2['dpr'], self.stats_to_values2['hs'])

        # Если в профиле игрока нет статистики за последние 3 месяца
        except IndexError:
            print('Please do not try to compare players with no stats by past 3 months')
            print('Waiting 10 seconds before exiting')
            time.sleep(10)
            sys.exit()

        # Если Не удалось найти профиль игрока
        except AttributeError:
            if self.player_found is False:
                print('Could not find this player.\nPlease try again')
            else:
                print('Not enough stats to complete analysis.\nRerun the program and try again')
            print('Waiting 10 seconds before exiting')
            time.sleep(10)
            sys.exit()

    # Используя dll с кодом на C происходит вызов функции, рассчитывающей вероятность
    def print_probability_p(self):
        self.cfile.PlayerStatsFormula.argtypes = [ctypes.c_float] * 8
        self.cfile.PlayerStatsFormula.restype = ctypes.c_float
        print(f'\nAccording to my calculations:\n{self.stats_to_values1["nick"]} will beat'
              f' {self.stats_to_values2["nick"]} with probability',
              round(self.cfile.PlayerStatsFormula(self.stats_to_values1["rt"], self.stats_to_values2["rt"],
                                                  self.stats_to_values1["kpr"], self.stats_to_values2["kpr"],
                                                  self.stats_to_values1["dpr"], self.stats_to_values2["dpr"],
                                                  self.stats_to_values1["hs"], self.stats_to_values2["hs"]), 1), '%')
