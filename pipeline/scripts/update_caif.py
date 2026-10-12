import openpyxl, re, sys
sys.path.insert(0,'scripts')
from deflators import A
from openpyxl.utils import get_column_letter as L
new=openpyxl.load_workbook('raw/SP_Fi_AX01.xlsx',data_only=True).worksheets[0]
wb=openpyxl.load_workbook('/home/claude/in/58287fbc-CAIFdeuda.xlsx')
ws=wb['dataset- CAIF corriente']
for mr in list(ws.merged_cells.ranges): ws.unmerge_cells(str(mr))
for r in range(2,41):
    for c in range(1,33):
        v=new.cell(r-1,c).value
        if v=='-': v=0
        ws.cell(r,c).value=v
ws.cell(2,1).value=new.cell(1,1).value
ws.cell(42,1).value='Actualizado 12/10/2026 con IDECBA SP_Fi_AX01 (1995/2025*). 2025* provisorio.'
# ipc: tasas promedio anual IPCBA (2013+) / serie original (antes), base promedio 2026
ip=wb['ipc']
ip.cell(1,2).value='tasa (var. promedio anual; IPCBA desde 2014)'
for i,y in enumerate(range(1990,2027)):
    r=2+i
    ip.cell(r,1).value=y
    if y>=1996: ip.cell(r,2).value=float(A[y]/A[y-1]-1)
    ip.cell(r,3).value=f'=B{r}+1'
    ip.cell(r,4).value=f'=PRODUCT(C{r+1}:$C$38)' if y<2026 else 1
ip.cell(40,1).value='Base: pesos promedio 2026. 2014-2026: IPCBA (IDECBA), promedio anual; oct-dic 2026 proyectado al 2% mensual. 1996-2013: serie original del archivo.'
# constante: agregar 2025 en columna AF
cs=wb['constante']
cs.cell(1,32).value=2025
for r in range(2,39):
    f=cs.cell(r,31).value
    if isinstance(f,str) and f.startswith('='):
        cs.cell(r,32).value=f.replace("'dataset- CAIF corriente'!AE","'dataset- CAIF corriente'!AF").replace('constante!AE$1','constante!AF$1')
for r in range(39,90):
    f=cs.cell(r,31).value
    if isinstance(f,str) and f.startswith('='):
        cs.cell(r,32).value=re.sub(r'\bAE(\d+)',r'AF\1',f)
cs.cell(1,1).value='billones de pesos promedio 2026 (IPCBA)'
wb.save('/home/claude/out/CAIF_deuda_actualizado.xlsx')
print('ok', cs.cell(2,32).value)
