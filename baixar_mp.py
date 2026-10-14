import importlib.util,sys,os
sp=importlib.util.spec_from_file_location('b','/media/hitsuzen/Novo volume/money/baixar_portal_v2.py'); b=importlib.util.module_from_spec(sp); sp.loader.exec_module(b)
fila=b.fila_judiciario(2016,2026,'/media/hitsuzen/Novo volume/money/dados_portal',True)
fila=[x for x in fila if not os.path.exists(x[1])]
print(len(fila),'pacotes novos',flush=True)
b.executar(fila,(0.3,0.8),4)
