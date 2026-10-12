import json, os
D=json.load(open('data2.json'))
neg=open('logo_neg.datauri').read(); pos=open('logo_pos.datauri').read()
def build(tpl,data,out):
    t=open(tpl).read()
    s=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    t=t.replace('__LOGO_NEG__',neg).replace('__LOGO_POS__',pos).replace('__DATA__',s)
    open(out,'w').write(t); print(out, round(os.path.getsize(out)/1e6,2),'MB')
main={k:v for k,v in D.items() if k not in ('delitos','seg','logo_neg','logo_pos')}
build('site/template_main.html',main,'site/presupuesto-caba-2027.html')
G=D['G']; gd=G['dims']; fi=gd['fun_desc'].index('Seguridad interior'); am=gd['inc_desc'].index('Amortización de deuda')
last26=max(r[1] for r in G['rows'] if r[0]==2026)
dev={}; v26=0
for r in G['rows']:
    if r[3]!=fi or r[4]==am: continue
    if r[1]==4: dev[str(r[0])]=dev.get(str(r[0]),0)+r[9]
    if r[0]==2026 and r[1]==last26: v26+=r[8]
seg={k:D[k] for k in ('defl','ipcm','caif','p2027_fun','seg','delitos')}
seg['seggasto']={'dev':dev,'v26':v26}
build('site/template_seg.html',seg,'site/seguridad-caba.html')
