import pandas as pd
import numpy as  np

pi = np.pi
# from step_1... None
# from step_2

def mult_row_by(o_data, multiply_values):
    """
        :param o_data: dados originalis
        :param multiply_values: valores que multiplicaram cada linha
        dos dados originais
        :return: tabela de dados onde cada cada valor de multiply_values
        multiplica uma linha dos dados originais
    """
    n_data = o_data
    for row in o_data.index:
        n_data.iloc[row, 1:] = multiply_values.loc[row] * o_data.iloc[row,1:]
    return n_data


horario = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx', sheet_name='Planilha1')
equipamentos = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx', sheet_name='Planilha2')
motores = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx', sheet_name='Planilha3')

cv2kw = .735499

e_n = equipamentos.loc[:, 'η (%)']
e_fp = equipamentos.loc[:, 'fp']
e_kVA = equipamentos.loc[:, 'kVA']

p_equipamentos = e_kVA * e_fp * e_n
s_equipametnos = e_kVA * e_n

m_cv = motores.loc[:, 'cv']
m_n = motores.loc[:, 'η (%)']
m_fp = motores.loc[:, 'fp']

p_motor = (m_cv * cv2kw * m_fp) / m_n
s_motor = (m_cv * cv2kw) / m_n

potencia_p_diaria = pd.concat([p_equipamentos, p_motor]).reset_index(drop=True)
potencia_s_diaria = pd.concat([s_equipametnos, s_motor]).reset_index(drop=True)

# tabela de consumo diario
consumo_diario = mult_row_by(horario[:], potencia_p_diaria)

# para os transformadores
transformador_1 = mult_row_by(horario[:], potencia_s_diaria[:])[:9]
transformador_2 = mult_row_by(horario[:], potencia_s_diaria[:])[9:]

cd_max = consumo_diario.max()
t1_max = transformador_1.max()
t2_max = transformador_2.max()

# usado para o plot
cd = consumo_diario[:].iloc[:, 1:].sum()
t1 = transformador_1[:].iloc[:, 1:].sum()
t2 = transformador_2[:].iloc[:, 1:].sum()

# para visualizar as variaveis importantes, como elas se organizam e se estruturam
def s1_variables():
    print(f"""\033[33mHorario original\033[m
{horario.to_string()}\n
\033[33mEquipamentos\033[m
{equipamentos.to_string()}\n
\033[33mMotores\033[m
{motores.to_string()}\n
\033[33mPotência (P) dos equipamentos\033[m
{p_equipamentos.to_string()}\n
\033[33mPotência (S) dos equipamentos\033[m
{s_equipametnos.to_string()}\n
\033[33mPotência (P) dos motores\033[m
{p_motor.to_string()}\n
\033[33mPotência (S) dos motores\033[m
{s_motor.to_string()}\n
\033[33mPotência (P) dirária completa\033[m
{potencia_p_diaria.to_string()}
\033[33mPotência (S) dirária completa\033[m
{potencia_s_diaria.to_string()}
\033[33mPotência dirária consumida\033[m
{consumo_diario.to_string()}
\033[33mPotência dos tranformadores\033[m
\033[32mTransformador 1\033[m
{transformador_1}
\033[32mTransformador 2\033[m
{transformador_2}
\033[34mCd\033[m
{cd}
\033[34mT1\033[m
{t1}
\033[34mT2\033[m
{t2}
""")

# from step3()


