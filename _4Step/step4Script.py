import matplotlib.pyplot as plt
from CurvaDeCarga._2Step.step2Script import transformador_1, transformador_2

'''
    < Objetivos >
        -- Gráfico da curva de carga [x]
'''

fig, axs = plt.subplots()

axs.plot(transformador_1)
axs.plot(transformador_2)
plt.show()