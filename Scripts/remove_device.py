from CurvaDeCarga.Merge.functions import CurvaDCarga

cdg = CurvaDCarga()
cdg.remove_device('qwe2')  # dispositivo q não tem nos dados
cdg.remove_device('QL2')  # dispositivo q tem nos dados
cdg.remove_device()  # nenhum dispositivo especificado
cdg.show_vars()
