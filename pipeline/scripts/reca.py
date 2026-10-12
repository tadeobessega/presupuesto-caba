import re
import openpyxl, pandas as pd
ws=openpyxl.load_workbook('raw/SP_IP_Reca_concepto.xlsx',data_only=True).worksheets[0]
rows=list(ws.iter_rows(values_only=True))
cols=['total','iibb','abl','patentes','sellos','planes','publicidad','otros']
meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
y=None; out=[]
for r in rows[2:]:
    if isinstance(r[0],int) and r[1] is None: y=1997 if y is None else y+1; continue
    if isinstance(r[0],str) and y:
        mm=re.sub(r'[\d\s\*]','',r[0])
        if mm in meses:
            vals=[float(x) if isinstance(x,(int,float)) else 0.0 for x in r[1:9]]
            out.append([y,meses.index(mm)+1]+vals)
df=pd.DataFrame(out,columns=['año','mes']+cols)
df.to_pickle('reca.pkl'); print(df.tail(3)); print(df.groupby('año').total.sum().tail(4))
