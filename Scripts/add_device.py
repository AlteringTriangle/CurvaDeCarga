from CurvaDeCarga.Merge.functions import CurvaDCarga

cdg = CurvaDCarga()

rd = {'00:00': 0, '01:00': 0, '02:00': 0, '03:00': 1, '04:00': 1, '05:00': 0, '06:00': 0, '07:00': 0, '08:00': 1,
      '09:00': 1, '10:00': 1, '11:00': 0, '12:00': 0, '13:00': 0, '14:00': 0, '15:00': 1, '16:00': 0, '17:00': 0,
      '18:00': 1, '19:00': 1, '20:00': 0, '21:00': 0, '22:00': 1, '23:00': 0}

# adicionando um motor, com um horario predefinidos
cdg.add_device(mode='nd',nm='M9',desc='Motor 9', alt=88, n=.95, fp=.85, hr=rd)
# adicionadno um equipametno, com um horário predefinidos
cdg.add_device(mode='nd',nm='Aq12',desc='Sistema de aquecimento 12', alt=6, n=.95, fp=.85, hr=rd)
# cdg.add_device(mode='wr')  # dados são fornecidos pelo prompt, dados tanto de horario como de equipamentos
cdg.show_vars()
