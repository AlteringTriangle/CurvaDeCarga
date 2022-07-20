import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Objetivos
    --- incializar o dataframe [x]
    --- calcular as potencias diarias, ativa e aparente [x]
    --- plotar os gráficos da curva de carga e dimensionamento dos transformadores[x]
    --- funções para modificar o horário [x]
    --- modo rd/random_data, para gerar um horário aleatório para um equipamento [x]
    --- modo nd/new_data, para usar dados já obtidos [x]
    --- modo wr/write, escrever pelo prompt o novo horario [x]
    --- modo +inteligente de identificar o transformador 1 e 2 [x]
    --- função p/ modificar, adicionar e retirar equipamentos, que também os mantenha organizado [x]
    --- por algum motivo, os valores das potências abaixaram, descobrir pq e resolver [x]
    *** problema *** a potencia dos transformadores deram uma invertida, pois os AQ fazem parte do t1
"""

class CurvaDCarga:
    def __init__(self):
        self.horario = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                     sheet_name='Planilha1').sort_values(by='Equipamento').reset_index(drop=True)
        self.equipamentos = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                          sheet_name='Planilha2').sort_values(by='Equipamento').reset_index(drop=True)
        self.motores = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                     sheet_name='Planilha3').sort_values(by='Equipamento').reset_index(drop=True)

        self.sep = self.find_t1xt2()  # [e] equipamentos / [m] motores / [t1] transf 1 / [t2] transf [2]
        self.equipamentos.index = self.sep['e']
        self.motores.index = self.sep['m']
        self.cv2kw = .735499
        self.cd, self.t1, self.t2, self.cd_max, self.t1_max, self.t2_max = [None, ] * 6
        self.calc_potencias()

    def mult_row_by(self, multiply_values):
        """
            :param multiply_values: valores que multiplicaram cada linha
            dos dados originais
            :return: tabela de dados onde cada cada valor de multiply_values
            multiplica uma linha dos dados originais
        """
        n_data = self.horario.copy()
        for row in n_data.index:
            n_data.iloc[row, 1:] = multiply_values.loc[row] * n_data.iloc[row, 1:]
        return n_data

    def calc_potencias(self):

        e_n = self.equipamentos.loc[:, 'η (%)']
        e_fp = self.equipamentos.loc[:, 'fp']
        e_kVA = self.equipamentos.loc[:, 'kVA']

        p_equipamentos = e_kVA * e_fp * e_n
        s_equipamentos = e_kVA * e_n
        p_equipamentos.index = self.sep['e']
        s_equipamentos.index = self.sep['e']

        m_cv = self.motores.loc[:, 'cv']
        m_n = self.motores.loc[:, 'η (%)']
        m_fp = self.motores.loc[:, 'fp']

        p_motor = (m_cv * self.cv2kw * m_fp) / m_n
        s_motor = (m_cv * self.cv2kw) / m_n
        p_motor.index = self.sep['m']
        s_motor.index = self.sep['m']

        potencia_p_diaria = pd.concat([p_equipamentos, p_motor])
        potencia_s_diaria = pd.concat([s_equipamentos, s_motor])

        # tabela de consumo diario (P)
        consumo_diario = self.mult_row_by(potencia_p_diaria)

        # para os transformadores (S)
        transformador_1 = self.mult_row_by(potencia_s_diaria[:]).loc[self.sep['t1']]
        transformador_2 = self.mult_row_by(potencia_s_diaria[:]).loc[self.sep['t2']]

        # usado para o plot
        self.cd = consumo_diario[:].iloc[:, 1:].sum()
        self.t1 = transformador_1[:].iloc[:, 1:].sum()
        self.t2 = transformador_2[:].iloc[:, 1:].sum()

        self.cd_max = self.cd.max()
        self.t1_max = self.t1.max()
        self.t2_max = self.t2.max()

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

    def change_horario(self, mode='rd', data=None):
        """
        :param mode: rd -> horário aleatório
                     nd -> dados já especificado
                     wr -> escrever novos dados pelo prompt
        :return: modificia diretamente self.horario
        """
        if mode.lower() == 'rd':
            choice = self.ask_device()
            time_on = self.use_data(self.random_data())
            print(f'Changing {choice} timetable to\n{time_on}')
            self.change_timing(choice, time_on)
        elif mode.lower() == 'nd':
            if data:
                choice = self.ask_device()
                time_on = self.use_data(data)
                print(f'Changing {choice} timetable to\n{time_on}')
                self.change_timing(choice, time_on)
            else:
                print('Nenhum dado especificado em *data*')
        elif mode.lower() == 'wr':
            choice = self.ask_device()
            time_on = self.ask_horario()
            print(f'Changing {choice} timetable to\n{time_on}')
            self.change_timing(choice, time_on)
        else:
            print('Modo não reconhecido...')
            return
        self.calc_potencias()

    def ask_horario(self):
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
            while not n.isnumeric():
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

        devices = list(self.horario[:].iloc[:, 0])
        print(f'Available devices are:')
        for i, device in enumerate(devices[:-1]):
            if (i + 1) % 8 == 0:
                print(f'{device}', end=',\n')
            else:
                print(f'{device}', end=', ')
        print(f'{devices[-1]}.')
        choice = input('choice one to modify (name or position number)')
        if choice.isdigit():
            choice = self.horario[:].iloc[int(choice) - 1, 0]
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
        line = self.horario.loc[self.horario.iloc[:, 0] == choice]
        newtime['Equipamento'] = choice
        line = pd.DataFrame(newtime, index=line.index)
        self.horario.loc[line.index] = line

    def add_device(self, mode='wr',nm=None, desc=None, alt=None, n=None, fp=None, hr=None):
        if mode == 'wr':
            nm = input('Identificador **(Inicial [M] reservada a motores)**\n').upper()
            desc = input('Descrição\n').capitalize()
            if nm[0] == 'M':
                alt = input('Cavalos\n')
                new_line = {'Equipamento': str(), 'Descrição': str(), 'cv': float(),
                            'η (%)': float(), 'fp': float()}
                nl_id = self.motores.index[-1]
            else:
                alt = input('Kva\n')
                new_line = {'Equipamento': str(), 'Descrição': str(),
                            'kVA': float(), 'η (%)': float(), 'fp': float()}
                nl_id = self.equipamentos.index[-1]

            n = input('Eficiência\n')
            fp = input('Fator de potência\n')

            alt = alt.replace(',', '.')
            n = n.replace(',', '.')
            fp = fp.replace(',', '.')

            dados = [nm, desc, float(alt), float(n), float(fp)]
            for i,key in enumerate(new_line.keys()):
                new_line[key] = dados[i]

        elif mode == 'nd':
            if nm[0] == 'M':
                new_line = {'Equipamento': str(), 'Descrição': str(), 'cv': float(),
                            'η (%)': float(), 'fp': float()}
                nl_id = self.motores.index[-1]
            else:
                new_line = {'Equipamento': str(), 'Descrição': str(),
                            'kVA': float(), 'η (%)': float(), 'fp': float()}
                nl_id = self.equipamentos.index[-1]

            dados = [nm.upper(), desc.capitalize(), float(alt), float(n), float(fp)]
            for i, key in enumerate(new_line.keys()):
                new_line[key] = dados[i]

        else:
            return

        if not hr:
            hr = self.ask_horario()

        hr_line = {'Equipamento': dados[0]}
        for k, v in hr.items():
            hr_line[k] = v

        dhr = pd.DataFrame(hr_line, index=[self.horario.index[-1]+1])
        dnl = pd.DataFrame(new_line, index=[nl_id+1])

        # print(new_line)
        self.horario = pd.concat([self.horario[:], dhr]).sort_values(by='Equipamento').reset_index(drop=True)
        # print(f'Novo horario adicionado\n{self.horario}')
        if dados[0][0] == 'M':
            self.motores = pd.concat([self.motores[:], dnl]).sort_values(by='Equipamento').reset_index(drop=True)
            # print(f'Um motor foi adicionado\n{self.motores}')
        else:
            self.equipamentos = pd.concat([self.equipamentos[:], dnl]).sort_values(by='Equipamento').reset_index(drop=True)
            # print(f'Um equipamento foi adicionado\n{self.equipamentos}')
        self.sep = self.find_t1xt2()
        self.calc_potencias()
        # print(f'Novo consumo diario\n{self.cd}')

    def remove_device(self, device=None):
        print(f'\033[31mWarning, you are removing a device\033[m')
        if not device:
            device = self.ask_device()
            if not device:
                return print('Nenhum dado removido')
        verify = self.horario.loc[:, 'Equipamento'] == device
        id_tr = self.horario.loc[verify]
        if id_tr.empty:
            return print(f'{device} não foi encontrado')
        id_tr = id_tr.index[0]
        self.horario.drop(index=id_tr, inplace=True)
        self.horario.reset_index(inplace=True, drop=True)

        if id_tr in self.sep['e']:
            print(self.equipamentos)
            self.equipamentos.drop(index=id_tr, inplace=True)
        else:
            self.motores.drop(index=id_tr, inplace=True)
        self.sep = self.find_t1xt2()
        self.calc_potencias()

    def find_t1xt2(self):
        check_m = self.horario.loc[:, 'Equipamento'].str.startswith('M')
        check_aq = self.horario.loc[:, 'Equipamento'].str.startswith('AQ')
        check_t1 = check_m + check_aq
        t1_id = self.horario.loc[check_t1].index
        t2_id = self.horario.loc[~check_t1].index
        e_id = self.horario.loc[~check_m].index
        m_id = self.horario.loc[check_m].index
        return {'m': m_id, 'e': e_id, 't1': t1_id, 't2': t2_id}




cdg = CurvaDCarga()
# print(f'{cdg.cd_max}\n{cdg.t1_max}\n{cdg.t2_max}\n\n')

