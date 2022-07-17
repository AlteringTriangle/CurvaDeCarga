import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

'''
    < Objetivos >
        -- Suavizar o gráfico da curva de carga [x]
        -- Suavizar multiplos gráficos []
'''

def suavizalinha(data, s, powerof, pg, per=10):
    step = pd.date_range(data.index[s], data.index[s+1], periods=per).strftime('%H:%M')
    delta = data[s] - data[s+1]

    if delta == 0:
        new_data = pd.DataFrame([data[s], ]*per, index=step)
        return new_data
    rng = np.arange(0, abs(delta)+abs(delta)/per, abs(delta)/(per-1))

    # temos um range de valores, que são os espaços equidistantes entre data[A] e data[b]
    # esse range tem o crescimento modificado quando multiplicado por uma função antes de ser
    # somado aos dados
    if delta > 0:
        a = pd.Series(powerof, index=step)
        a = -a
    else:
        # pg
        a = pd.Series(pg, index=step)

    new_data = data[s]+rng*a
    return new_data

def suavizadados(data, per=10):
    lr = 0
    d = data[lr:lr]

    q = per / (per + 1)
    powerof = np.arange(0, 1 + 1 / per, 1 / (per - 1))
    powerof = powerof ** q
    pg = list()
    a1 = 1 / q ** (per - 1)
    for c in range(0, per):
        pg.append(a1 * q ** c)

    for rowid in range(0,len(data.index[:-1])):
        f = suavizalinha(data, rowid,powerof, pg, per)
        d = pd.concat([d, f, data[rowid+1:rowid+1]])
    return d

def smoothg(data, title=None, legend=None, xlabel=None, ylabel=None, y_data=None):

    if ':' in str(data.index[0]):
        # index = daterange
        xtick = pd.date_range(str(data.index[0]), str(data.index[-1]), freq="H").strftime('%H:%M')
    else:
        # index = index
        xtick = data.index

    fig, axs = plt.subplots(1)
    axs.plot(suavizadados(data, per=10))
    axs.plot(data, marker='o', linestyle='None')
    axs.set_xticks(xtick)
    plt.title(title)
    plt.legend(legend)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    plt.show()
