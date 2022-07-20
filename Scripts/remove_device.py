from CurvaDeCarga.Merge.functions import CurvaDCarga

cdg = CurvaDCarga()
# dispositivo q não tem nos dados, nada é removido
cdg.remove_device('qwe2')
# dispositivo q tem nos dados, ele é removido
cdg.remove_device('QL2')
# nenhum dispositivo especificado, pelo prompt pode-se escolher um
# dispositivo a se remover
cdg.remove_device()
cdg.show_vars()
