import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CurvaDCarga:
    def __init__(self):
        self.horario = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                     sheet_name='Planilha1')
        self.equipamentos = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                          sheet_name='Planilha2')
        self.motores = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                     sheet_name='Planilha3')

        self.cv2kw = .735499
        self.cd, self.t1, self.t2, self.cd_max, self.t1_max, self.t2_max = [None, ] * 6
        self.calc_potencias()

    def mult_row_by(self, multiply_values):
        """
            :param o_data: dados originais
            :param multiply_values: valores que multiplicaram cada linha
            dos dados originais
            :return: tabela de dados onde cada cada valor de multiply_values
            multiplica uma linha dos dados originais
        """
        n_data = self.horario[:]
        for row in n_data.index:
            n_data.iloc[row, 1:] = multiply_values.loc[row] * n_data.iloc[row, 1:]
        return n_data

    def calc_potencias(self):
        e_n = self.equipamentos.loc[:, 'η (%)']
        e_fp = self.equipamentos.loc[:, 'fp']
        e_kVA = self.equipamentos.loc[:, 'kVA']

        p_equipamentos = e_kVA * e_fp * e_n
        s_equipametnos = e_kVA * e_n

        m_cv = self.motores.loc[:, 'cv']
        m_n = self.motores.loc[:, 'η (%)']
        m_fp = self.motores.loc[:, 'fp']

        p_motor = (m_cv * self.cv2kw * m_fp) / m_n
        s_motor = (m_cv * self.cv2kw) / m_n

        potencia_p_diaria = pd.concat([p_equipamentos, p_motor]).reset_index(drop=True)
        potencia_s_diaria = pd.concat([s_equipametnos, s_motor]).reset_index(drop=True)

        # tabela de consumo diario (P)
        print(potencia_p_diaria)
        consumo_diario = self.mult_row_by(potencia_p_diaria)

        # para os transformadores (S)
        transformador_1 = self.mult_row_by(potencia_s_diaria[:])[:9]
        transformador_2 = self.mult_row_by(potencia_s_diaria[:])[9:]

        self.cd_max = consumo_diario.max()
        self.t1_max = transformador_1.max()
        self.t2_max = transformador_2.max()

        # usado para o plot
        self.cd = consumo_diario[:].iloc[:, 1:].sum()
        self.t1 = transformador_1[:].iloc[:, 1:].sum()
        self.t2 = transformador_2[:].iloc[:, 1:].sum()

        # para visualizar as variaveis importantes, como elas se organizam e se estruturam

    def plot_data(self):
        fig1, ax1 = plt.subplots()
        xtick = pd.date_range(str(self.cd.index[0]), str(self.cd.index[-1]), freq="2H").strftime('%H:%M')

        ax1.plot(self.cd[:])
        ax1.set_xticks(xtick)
        ax1.legend('Curva de carga')
        plt.xlabel('Horário')
        plt.ylabel('Potência kW')
        ax1.grid()

        fig2, ax2 = plt.subplots()

        ax2.plot(self.t1[:])
        ax2.plot(self.t2[:])
        ax2.set_xticks(xtick)
        ax2.legend('Dimensionamento dos Transformadores')
        plt.xlabel('Horário')
        plt.ylabel('Potência kVA')
        ax2.grid()
        plt.show()

    def change_horario(self, mode='rd'):
        """
        :param mode: rd -> horário aleatório
        :return: modificia diretamente self.horario
        """
        if mode.lower() == 'rd':
            choice = self.ask_device()
            time_on = self.use_data(self.random_data())
            self.change_timing(choice, time_on)

    def ask_data(self):
        """
        O usuario digita pelo prompt a maneira que o horário
        está organizado
        :return: dicionario pronto para ser transformado em df/s
        """
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

    def use_data(self, data):
        """
        :param data: parametro de dados já organizados afim de virar
        um horario
        :return: dicionario pronto para ser transformado em df/s
        """

        d = dict()
        for c in range(0, 24):
            ind = c
            if c <= 9:
                c = f'0{c}:00'
            else:
                c = f'{c}:00'

            d[c] = data[ind]

        return d

    def random_data(self, size=24):
        """
        :param size: numero de divisões do horario
        :return: uma lista aleatoria, de zeros e uns para representar o horario
        """
        rd = np.random.randint(0, 2, size)
        return rd

    def ask_device(self):

        devices = list(self.horario.iloc[:, 0])
        print(f'Available devices are:')
        for i, device in enumerate(devices[:-1]):
            if (i + 1) % 8 == 0:
                print(f'{device}', end=',\n')
            else:
                print(f'{device}', end=', ')
        print(f'{devices[-1]}.')
        choice = input('choice one to modify (name or position number)')
        if choice.isdigit():
            choice = self.horario.iloc[int(choice) - 1, 0]
        else:
            choice = choice.upper()
            if choice not in devices:
                choice = None
        if choice:
            print(f'you choice was {choice}')
        else:
            print(f'your choice isn\'t in avaliable devices')
        return choice

    def change_timing(self, choice, newtime):
        """
        :param choice: equipamento a ser modificado
        :param newtime: novo horario para o equipamento
        :return: self.horario é atualizado
        """
        print('\033[33mold data\033[m'.capitalize())
        print(self.horario)
        line = self.horario.loc[self.horario.iloc[:, 0] == choice]
        newtime['Equipamento'] = choice
        line = pd.DataFrame(newtime, index=line.index)
        self.horario.loc[line.index] = line
        print('\033[33mmodified data\033[m'.capitalize())
        print(self.horario)


cdg = CurvaDCarga()
cdg.plot_data()
