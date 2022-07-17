import pandas as pd
import numpy  as np

'''
    < Objetivos >
        -- Analisar a potência que cada equipamento utiliza e lista-las em um dataframe/series [x]
        -- Calcular o consumo diário, se baseando no horário de funcionamento dos equipamentos [x]
'''



horario = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx', sheet_name='Planilha1')
equipamentos = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx', sheet_name='Planilha2')
motores = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx', sheet_name='Planilha3')

cv2kw = .735499

def linexseries(a, b):
    for row in a.index:
        a.iloc[row,1:] = b.loc[row]*a.iloc[row,1:]
    return a

def consumoD():
    return consumo_diario


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

# drop will drop old index column
# -- Analisar a potência que cada equipamento utiliza e lista-las em um dataframe/series
p_full = pd.concat([p_equipamentos, p_motor]).reset_index(drop=True)
s_full = pd.concat([s_equipametnos, s_motor]).reset_index(drop=True)

#--Calcular o consumo diário, se baseando no horário de funcionamento dos equipamentos

p_h = linexseries(horario[:], p_full)
consumo_diario = p_h.iloc[:,1:].cumsum().iloc[-1]

#--Calcular o consumo da potencia dos transformadores, vinculado ao quarto passo

s_h = linexseries(horario[:], s_full)

transformador_1 = s_h.iloc[:9,1:].cumsum().iloc[-1]
transformador_2 = s_h.iloc[9:,1:].cumsum().iloc[-1]

cd_max = consumo_diario.max()
t1_max = transformador_1.max()
t2_max = transformador_2.max()
