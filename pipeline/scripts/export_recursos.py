import pandas as pd, openpyxl, sys
sys.path.insert(0,'scripts')
from deflators import A, Q
R=pd.read_pickle('recursos.pkl')
q=R['q']; reca=R['reca']
# CAIF annual
ws=openpyxl.load_workbook('raw/SP_Fi_AX01.xlsx',data_only=True).worksheets[0]
rows=list(ws.iter_rows(values_only=True))
years=[int(str(y).replace('*','')) for y in rows[1][1:32]]
caif=pd.DataFrame({r[0].strip():[0 if v=='-' else v for v in r[1:32]] for r in rows[2:39] if r[0]},index=years)
caif.to_pickle('caif.pkl')
an=q.groupby('año').agg({c:'sum' for c in q.columns[2:9]})
an['n_trim']=q.groupby('año').size()
an=an[an.n_trim==4].drop(columns='n_trim')
an=an.join(caif[['Ingresos tributarios','6) Recursos totales (1+4)']].rename(columns={'Ingresos tributarios':'CAIF tributarios','6) Recursos totales (1+4)':'CAIF recursos totales'}))
an['RON (CAIF tributarios − recaudación propia)']=an['CAIF tributarios']-an['Recaudación propia']
real=an.copy()
for c in real.columns: real[c]=real[c]/real.index.map(A)/1e3
ra=reca.groupby('año')[['Total','IIBB','ABL','Patentes','Sellos','Planes de facilidades','Publicidad','Gravámenes varios']].sum()
ra['meses']=reca.groupby('año').size()
with pd.ExcelWriter('/home/claude/out/recursos_CABA_consolidado.xlsx') as w:
    pd.DataFrame({'nota':[
     'Recursos = Recaudación propia + No tributarios + Recursos de capital + Rentas de la propiedad + Transferencias corrientes + Venta de bienes y servicios (+ RON).',
     'Recaudación propia: IDECBA SP_IP_Reca_concepto (mensual, ene-1997/ago-2026). Resto: IDECBA importe realizado trimestral acumulado (1T2007/2T2026), convertido a flujos trimestrales.',
     'RON (coparticipación) no se difunde trimestralmente: se estima anual como CAIF ingresos tributarios − recaudación propia.',
     'Desde 3T2024 Transferencias corrientes incluye la transferencia a cuenta del fallo CSJN (Exp. 1865/2020) por el diferencial de coparticipación.',
     'Valores en millones de pesos corrientes; hoja "anual_real" en miles de millones de pesos promedio 2026 (IPCBA).',
     'Descargado 12/10/2026.']}).to_excel(w,sheet_name='esquema',index=False)
    q.to_excel(w,sheet_name='consolidado_trimestral',index=False)
    an.to_excel(w,sheet_name='consolidado_anual')
    real.round(1).to_excel(w,sheet_name='anual_real')
    reca.to_excel(w,sheet_name='reca_mensual',index=False)
    ra.to_excel(w,sheet_name='reca_anual')
    for k,v in R['acc'].items(): v.to_excel(w,sheet_name=('acum_'+k)[:31],index=False)
print(real.round(0).tail(8).to_string()); print(ra.tail(3))
