import matplotlib.pyplot as plt
from .._2Step.step2Script import consumo_diario
from suavizargrafico import smoothg

'''
    < Objetivos >
        -- Gráfico da curva de carga [x]
'''

smoothg(consumo_diario,'Curva de carga','Potência kW','Horário','kW')


