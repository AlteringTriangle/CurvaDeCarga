import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Objetivos
    --- adaptar melhor as funções para se adequar aos scripts
"""

class CurvaDCarga:
    def __init__(self):
        self.horario = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                     sheet_name='Planilha1').sort_values(by='Equipamento').reset_index(drop=True)
        self.equipamentos = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                          sheet_name='Planilha2').sort_values(by='Equipamento').reset_index(drop=True)
        self.motores = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                                     sheet_name='Planilha3').sort_values(by='Equipamento').reset_index(drop=True)

        self.cv2kw = .735499

        self.sep = self.find_t1xt2()
        self.cd, self.t1, self.t2, self.cd_max, self.t1_max, self.t2_max = [None, ] * 6
        self.cd_coord, self.t1_coord, self.t2_coord = [None, ] * 3

        self.start()

    def start(self):
        """
            -> separa o transformador 1 do dois;
            -> indexa os dataframes [equipamento] e [motores] para se igualar ao indice de [horario]
            -> zera os dados, e então calcula as potências
        """
        self.sep = self.find_t1xt2()  # [e] equipamentos / [m] motores / [t1] transf 1 / [t2] transf [2]
        self.equipamentos.index = self.sep['e']
        self.motores.index = self.sep['m']
        self.cd, self.t1, self.t2, self.cd_max, self.t1_max, self.t2_max = [None, ] * 6
        self.cd_coord, self.t1_coord, self.t2_coord = [None, ] * 3
        self.calc_potencias()

    def show_vars(self):
        """
            -> mostra variaveis importantes na tela
        """
        print(f'\n\033[34mHorário\033[m\n{self.horario.to_string()}')
        print(f'\n\033[34mConsumo Diário\033[m\n{self.cd}')
        print(f'\n\033[34mTransformador 1\033[m\n{self.t1}')
        print(f'\n\033[34mTransformador 2\033[m\n{self.t2}')
        print(f'Max em consumo diario -> {self.cd_max}')
        print(f'Max no transformador 1 -> {self.t1_max}')
        print(f'Max no transformador 2 -> {self.t2_max}')

    def mult_row_by(self, multiply_values):
        """
            :param multiply_values: valores que multiplicaram cada linha
            dos dados originais
            horário terá cada linha multiplcada por cada linha de multiply_values
            que é uma unica coluna
        """
        n_data = self.horario.copy()
        for row in n_data.index:
            n_data.iloc[row, 1:] = multiply_values.loc[row] * n_data.iloc[row, 1:]
        return n_data

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
        quando aplicado em use_data, temos um dicionario aleatorio pronto para
        virar um dataframe
        """
        rd = np.random.randint(0, 2, size)
        return rd

    def ask_device(self):
        """
        :return: Retorna um dispositivo escolhido pelo usuario
        """

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
        if not choice:
            raise Exception(f'your choice isn\'t in avaliable devices')

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

    def find_t1xt2(self):
        """
            :return: dicionario contendo quais são os indicies de horario que separam equipamentos comuns
            de motores, e equipamentos do transformador 1 do transformador 2
            ** dependendo da lógica da organização dos equipamentos do transformador 1 e 2, sujeito
            a alterações
        """
        check_m = self.horario.loc[:, 'Equipamento'].str.startswith('M')
        check_aq = self.horario.loc[:, 'Equipamento'].str.startswith('AQ')
        check_t1 = check_m + check_aq
        t1_id = self.horario.loc[check_t1].index
        t2_id = self.horario.loc[~check_t1].index
        e_id = self.horario.loc[~check_m].index
        m_id = self.horario.loc[check_m].index
        return {'m': m_id, 'e': e_id, 't1': t1_id, 't2': t2_id}

    #########################################################################

    def calc_potencias(self):

        # tabela equipamentos
        e_n = self.equipamentos.loc[:, 'η (%)']
        e_fp = self.equipamentos.loc[:, 'fp']
        e_kva = self.equipamentos.loc[:, 'kVA']

        p_equipamentos = e_kva * e_fp * e_n
        s_equipamentos = e_kva * e_n

        # tabela motores
        m_cv = self.motores.loc[:, 'cv']
        m_n = self.motores.loc[:, 'η (%)']
        m_fp = self.motores.loc[:, 'fp']

        p_motor = (m_cv * self.cv2kw * m_fp) / m_n
        s_motor = (m_cv * self.cv2kw) / m_n

        # potência de equipamentos + motores
        potencia_p_diaria = pd.concat([p_equipamentos, p_motor])
        potencia_s_diaria = pd.concat([s_equipamentos, s_motor])

        # tabela de consumo diario (P)
        consumo_diario = self.mult_row_by(potencia_p_diaria)

        # Tabela de consumo diario p/ os transformadores (S)
        transformador_1 = self.mult_row_by(potencia_s_diaria[:]).loc[self.sep['t1']]
        transformador_2 = self.mult_row_by(potencia_s_diaria[:]).loc[self.sep['t2']]

        # usado para o plot
        self.cd = consumo_diario[:].iloc[:, 1:].sum()
        self.t1 = transformador_1[:].iloc[:, 1:].sum()
        self.t2 = transformador_2[:].iloc[:, 1:].sum()

        # máximos de cada tabela
        self.cd_max = self.cd.max()
        self.t1_max = self.t1.max()
        self.t2_max = self.t2.max()

        # loc dos máximos
        cd_id = self.cd.loc[self.cd == self.cd.max()].index[0]
        h, m = int(cd_id[:2]), int(cd_id[3:])/60
        self.cd_coord = (h + m, self.cd_max)

        t1_id = self.t1.loc[self.t1 == self.t1.max()].index[0]
        h, m = int(t1_id[:2]), int(t1_id[3:])/60
        self.t1_coord = (h + m, self.t1_max)

        t2_id = self.t2.loc[self.t2 == self.t2.max()].index[0]
        h, m = int(t2_id[:2]), int(t2_id[3:])/60
        self.t2_coord = (h + m, self.t2_max)

        # (int(self.cd.loc[self.cd == self.cd.max()].index[0][:2])
        # self.cd.loc -> tabela original / p1
        # p1[self.cd == self.cd.max()]  tabela apenas com a linha do máximo /p2
        # p2.index -> indice onde o maximo se encontra, ainda index64 /p3
        # p3[0] indice onde o maximo se encontra, so que agora seu valor, e não seu index64 /p4
        # p4[:2], os dois primeiros numeros do indice são usados para as horas, e os dois ultimos
        # p/ os minutos, e entao, ** [:2] dois primeiros numeros, [2] dois pontos do horario [3:] dois ultimos /p5
        # int(p5) temos o numero do indice em x

    def plot_data(self):
        fig1, ax1 = plt.subplots()
        xtick = pd.date_range(str(self.cd.index[0]), str(self.cd.index[-1]), freq="2H").strftime('%H:%M')

        ax1.plot(self.cd[:])
        ax1.set_xticks(xtick)
        plt.title('Curva de carga')
        plt.legend('P')
        plt.xlabel('Horário')
        plt.ylabel('Potência kW')
        plt.annotate(self.cd_coord[1], xy=(self.cd_coord[0], self.cd_coord[1]),
                     xytext=(self.cd_coord[0] + 2, self.cd_coord[1] + 20),
                     arrowprops=dict(facecolor='black', shrink=0.05), )

        ax1.grid()

        fig2, ax2 = plt.subplots()

        ax2.plot(self.t1[:])
        ax2.plot(self.t2[:])
        ax2.set_xticks(xtick)
        plt.title('Dimensionamento dos transformadores')
        plt.legend(['T1', 'T2'])
        plt.xlabel('Horário')
        plt.ylabel('Potência kVA')
        plt.annotate(self.t1_coord[1], xy=(self.t1_coord[0], self.t1_coord[1]),
                     xytext=(self.t1_coord[0] + 2, self.t1_coord[1] + 20),
                     arrowprops=dict(facecolor='black', shrink=0.05), )
        plt.annotate(self.t2_coord[1], xy=(self.t2_coord[0], self.t2_coord[1]),
                     xytext=(self.t2_coord[0] + 2, self.t2_coord[1] + 20),
                     arrowprops=dict(facecolor='black', shrink=0.05), )
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
            self.change_timing(choice, time_on)
        elif mode.lower() == 'nd':
            if data:
                choice = self.ask_device()
                time_on = self.use_data(data)
                self.change_timing(choice, time_on)
            else:
                return print('Nenhum dado especificado em *data*')
        elif mode.lower() == 'wr':
            choice = self.ask_device()
            time_on = self.ask_horario()
            self.change_timing(choice, time_on)
        else:
            return print('Modo não reconhecido...')
        self.start()

    def add_device(self, mode='wr', nm=None, desc=None, alt=None, n=None, fp=None, hr=None):
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
            for i, key in enumerate(new_line.keys()):
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

        dhr = pd.DataFrame(hr_line, index=[self.horario.index[-1] + 1])
        dnl = pd.DataFrame(new_line, index=[nl_id + 1])

        self.horario = pd.concat([self.horario[:], dhr]).sort_values(by='Equipamento').reset_index(drop=True)
        if dados[0][0] == 'M':
            self.motores = pd.concat([self.motores[:], dnl]).sort_values(by='Equipamento').reset_index(drop=True)
        else:
            self.equipamentos = pd.concat([self.equipamentos[:], dnl]).sort_values(by='Equipamento').reset_index(
                drop=True)
        self.start()

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
            self.equipamentos.drop(index=id_tr, inplace=True)
        else:
            self.motores.drop(index=id_tr, inplace=True)
        self.start()


cdg = CurvaDCarga()
