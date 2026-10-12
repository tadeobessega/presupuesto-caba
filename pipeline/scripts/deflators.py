import openpyxl, pandas as pd, numpy as np
ws=openpyxl.load_workbook('raw/ipcba.xlsx',data_only=True).worksheets[0]
m=[(r[0],r[1]) for r in ws.iter_rows(values_only=True) if hasattr(r[0],'year') and r[1]]
ipc=pd.Series({pd.Timestamp(d):v for d,v in m}).sort_index()
PROJ_2026=0.020   # m/m oct-dic 2026 (supuesto)
DEC_2027=0.18     # pauta oficial dic/dic 2027
last=ipc.index[-1]; v=ipc.iloc[-1]
for i in range(1,16):
    d=last+pd.DateOffset(months=i)
    r=PROJ_2026 if d.year==2026 else (1+DEC_2027)**(1/12)-1
    v=v*(1+r); ipc[d]=v
ipc=ipc.sort_index()
ann=ipc.groupby(ipc.index.year).mean()
# antes de 2013: encadenar con la serie anual del usuario (tasas)
user={1995:0.01607754177045,1996:0.00054311344654056,1997:0.00327996924641338,1998:0.00664478929121004,1999:-0.0181046644835473,2000:-0.0073369945312316,2001:-0.0154342782205186,2002:0.40952868852458996,2003:0.0365632041869595,2004:0.0610098176718095,2005:0.123265036351619,2006:0.0983818770226537,2007:0.21520578071002197,2008:0.205985005170631,2009:0.18473658824159903,2010:0.270288609427305,2011:0.232755243759125,2012:0.23006037496028,2013:0.319438247105517}
idx={y:ann[y] for y in ann.index if y>=2013}
for y in range(2012,1994,-1):
    idx[y]=idx[y+1]/(1+user[y+1])
A=pd.Series(idx).sort_index()
A=A/A[2026]   # base: pesos promedio 2026
Q=ipc[ipc.index.year>=2019].groupby([ipc[ipc.index.year>=2019].index.year,(ipc[ipc.index.year>=2019].index.month-1)//3+1]).mean()
Q=Q/ann[2026]
if __name__=='__main__':
    print('avg27/avg26',ann[2027]/ann[2026]-1,' avg26/avg25',ann[2026]/ann[2025]-1,' dec25/dec24',ipc['2025-12-01']/ipc['2024-12-01']-1)
    print(A.round(5).tail(16).to_string()); print(Q.tail(8))
