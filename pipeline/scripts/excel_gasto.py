import pandas as pd, xlsxwriter
g=pd.read_pickle('gasto.pkl')
g['amortizacion']=(g.par_desc.fillna('').str.startswith('Amortizaci')|g.ppal_desc.fillna('').str.startswith('Disminución De Préstamos')).map({True:'Sí',False:'No'})
g['periodo']=g['año'].astype(str)+'-T'+g['trim'].astype(str)
cols=['año','trim','periodo','car','car_desc','jur','jur_desc','prog','prog_desc','fin','fin_desc','fun','fun_desc','inc','inc_desc','ppal','ppal_desc','par','par_desc','spar','spar_desc','fte','fte_desc','sancion','vigente','definitivo','devengado','amortizacion','fuente_dato']
g=g[cols].sort_values(['año','trim','jur','prog','inc','ppal','par','spar'])
wb=xlsxwriter.Workbook('out/base_gasto_CABA_trimestral_2019-2026.xlsx',{'constant_memory':True})
ws=wb.add_worksheet('base'); h=wb.add_format({'bold':True}); m=wb.add_format({'num_format':'#,##0'})
for j,c in enumerate(cols): ws.write(0,j,c,h)
for i,row in enumerate(g.itertuples(index=False),start=1):
    for j,v in enumerate(row):
        if isinstance(v,float):
            if v!=v: continue
            ws.write_number(i,j,v,m if j>=23 else None)
        else: ws.write(i,j,v)
nota=wb.add_worksheet('notas')
for i,t in enumerate(['Base de gasto CABA, apertura hasta partida subparcial, en pesos corrientes.',
 'Fuente: presupuesto ejecutado trimestral (data.buenosaires.gob.ar, CDN): 2019 T1-T4, 2020 T1, 2021 T2, 2022-2025 T1-T4, 2026 T1-T2. 2020 y 2021 T4 desde la base propia (Sheet1).',
 'Montos acumulados al trimestre (vigente y devengado). Sanción = crédito sancionado del año.',
 'Agregado por carácter, jurisdicción, programa, finalidad, función, inciso, principal, parcial, subparcial y fuente (sin UE, actividad, obra ni geo).',
 'Se eliminaron filas de totales de los CSV y se corrigieron montos en notación científica (2023 T1, 2024 T3 y T4). Definitivo = etapa definitiva (comprometido), también acumulado al trimestre.',
 'amortizacion = Sí: amortización de deuda dentro del inciso 7; excluir para comparar con el proyecto 2027.']): nota.write(i,0,t)
wb.close()
print(len(g))
