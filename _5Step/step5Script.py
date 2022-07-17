import pandas as pd
import numpy  as np

horario = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx', sheet_name='Planilha1')

def ask_data():
    d = dict()

    for c in range(0, 24):
        if c <= 9:
            c = f'0{c}:00'
        else:
            c = f'{c}:00'

        n = input(f'hora {c}')
        if int(n[:2]) > 0:
            n = 1
        else:
            n = 0
        d[c] = n
    return d

def use_data(data):
    d = dict()
    for c in range(0, 24):
        ind = c
        if c <= 9:
            c = f'0{c}:00'
        else:
            c = f'{c}:00'

        d[c] = data[ind]

    return d

def random_data(size=24):
    rd = np.random.randint(0, 2, size)
    return rd

def ask_device():

    devices = list(horario.iloc[:,0])
    print(f'Available devices are:')
    for i, device in enumerate(devices[:-1]):
        if (i+1) % 8 == 0:
            print(f'{device}', end=',\n')
        else:
            print(f'{device}', end=', ')
    print(f'{devices[-1]}.')
    choice = input('choice one to modify (name or position number)')
    if choice.isdigit():
        choice = horario.iloc[int(choice)-1, 0]
    else:
        choice = choice.upper()
        if choice not in devices:
            choice = None
    print(f'you choice was {choice}')
    return choice

def change_timing(data, choice, newtime):
    print('\033[33mold data\033[m'.capitalize())
    print(horario)
    line = data.loc[data.iloc[:, 0] == choice]
    newtime['Equipamento'] = choice
    line = pd.DataFrame(newtime, index=line.index)
    horario.loc[line.index] = line
    print('\033[33mmodified data\033[m'.capitalize())
    print(horario)


choice = ask_device()
time_on = use_data(random_data())
change_timing(horario, choice, time_on)
