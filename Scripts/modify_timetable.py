from CurvaDeCarga.Merge.functions import CurvaDCarga


nd = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
cdg = CurvaDCarga()
cdg.change_horario(mode='rd')  # horário aleatório
cdg.change_horario(mode='nd', data=nd)  # horario com dados predefinidos
# cdg.change_horario(mode='wr')  # inputs na tela recebem informações e geram o horario
cdg.show_vars()
