from gevent import monkey

# Фикс ошибки, возникающей при использовании grequests (PEP8 извини)
monkey.patch_all(thread=False, select=False)

from player_comparer import PlayerComparer
from team_comparer import TeamComparer
from stats_corrector import Corrector
from event_counter import Events
import sys
import os


# Создание dll библиотеки, если её ещё нет
if os.path.isfile('./probcount.dll') is False:
    os.system('gcc -fPIC -shared -o probcount.dll probability_counter.c')

# Создание экземпляров классов
PC = PlayerComparer()
TC = TeamComparer()
Corr = Corrector()
Evt = Events()
print('DO NOT try to compare teams/players without statistics by past 3 months!')

# Запуск цикла
while True:
    os.system('cls')

    # Пользователь выбирает одно из предложенных ему действий в каждом вводе
    question1 = input('1 - compare players\n'
                      '2 - compare teams\n'
                      '3 - stats corrector\n'
                      '4 - get events\n'
                      'input number -> ')

    # Если пользователь ввёл не то, что ему предлагалось
    if question1 not in ['1', '2', '3', '4']:
        print('There is no such option!')
        input('Press Enter to continue')
        os.system('cls')
        continue

    # Если Требуется увидеть анонсированные ивенты
    if question1 == '4':
        os.system('cls')
        Evt.get_events()
        Evt.print_events()
        Evt.input_event()
        Evt.print_event_info()
        Evt.print_probability_e()
        game_manager = input('\nPress Enter to continue or Q + Enter to exit -> ').lower()
        if game_manager == 'q':
            break
        os.system('cls')
        continue
    question2 = input('\nDo you want to use links(1) or names/nicknames(2) to search?\n-> ')

    # Если нужно сравнить игроков
    if question1 == '1':

        # Если нужно сравнить игроков, найдя их профили по ссылкам
        if question2 == '1':
            PC.input_player_links()

        # Если нужно сравнить игроков, найдя их профили по никнеймам
        elif question2 == '2':
            PC.input_nicknames()

        # Если пользователь ввёл что-то непонятное
        else:
            print('No such variant!')
            input('Press Enter to continue')
        os.system('cls')
        PC.print_player_stats()
        PC.print_probability_p()

    # Если нужно сравнить команды
    elif question1 == '2':

        # Если нужно сравнить команды, найдя профили по ссылкам
        if question2 == '1':
            TC.input_team_links()

        # Если нужно сравнить команды, найдя профили по названиям
        elif question2 == '2':
            TC.input_team_names()

        # Если пользователь ввёл что-то непонятное
        else:
            print('No such variant!')
            input('Press Enter to continue')
            continue
        os.system('cls')
        TC.print_team_stats()
        TC.print_probability_t()

    # Если нужно узнать количество матчей до исправления статистики
    elif question1 == '3':

        # Если нужно узнать количество матчей до исправления статистики, найдя профиль игрока по ссылке
        if question2 == '1':
            Corr.input_profile_link()

        # Если нужно узнать количество матчей до исправления статистики, найдя профиль игрока по его никнейму
        elif question2 == '2':
            Corr.input_player_nickname()

        # Если пользователь ввёл что-то непонятное
        else:
            print('No such variant!')
            input('Press Enter to continue')
            continue
        Corr.get_stat()
        Corr.correct()

    # Продолжить работу программы или выйти?
    game_manager = input('\nPress Enter to continue or Q + Enter to exit -> ').lower()
    if game_manager == 'q':
        sys.exit()
    os.system('cls')
