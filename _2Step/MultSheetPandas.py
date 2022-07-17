import pandas as pd

'''
    < Objetivos >
        -- Analisar uma tabela com informações em multiplas planilhas e como separa-las [x]
'''

horario = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                        sheet_name='Planilha1')
equipamentos = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                        sheet_name='Planilha2')
motores = pd.read_excel('../Dados Modificados/Tabela de dados de horarios e potencias.xlsx',
                        sheet_name='Planilha3')

# sheet_name pode ser o nome da planilha ou seu index, caseSensitive
# ultilizando o indice da planilha, o dataframe vem com {id: [...]}

print(horario)
print(equipamentos)
print(motores)