import json, os
D=json.load(open('data2.json'))
neg=open('logo_neg.datauri').read(); pos=open('logo_pos.datauri').read()
def build(tpl,data,out):
    t=open(tpl).read()
    s=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    t=t.replace('__LOGO_NEG__',neg).replace('__LOGO_POS__',pos).replace('__DATA__',s)
    open(out,'w').write(t); print(out, round(os.path.getsize(out)/1e6,2),'MB')
last26=max(r[1] for r in D['G']['rows'] if r[0]==2026)
lastM26=max(r[1] for r in D['reca']['rows'] if r[0]==2026)
main={k:v for k,v in D.items() if k not in ('delitos','seg','logo_neg','logo_pos')}
main.update(lastT26=last26,lastM26=lastM26,ymin=1995,aif2t=json.load(open('raw/aif_2t.json')),a27=json.load(open('analysis27.json')),p27jf=json.load(open('raw/p27_jur_fun.json')),percap=json.load(open('raw/dnap/percap.json')),comunas=json.load(open('raw/comunas/comunas.json')),pauta27=[[r['jcode'],r['prog'],r['ue'],r['v']/1e6] for r in json.load(open('p2027_prog.json')) if r['ppal'].lower().startswith('publicidad')])
build('site/template_main.html',main,'site/presupuesto-caba-2027.html')
G=D['G']; gd=G['dims']; fi=gd['fun_desc'].index('Seguridad interior'); am=gd['inc_desc'].index('Amortización de deuda')
last26=max(r[1] for r in G['rows'] if r[0]==2026)
dev={}; v26=0; s26=0; dt2={}
for r in G['rows']:
    if r[3]!=fi or r[4]==am: continue
    if r[1]==4: dev[str(r[0])]=dev.get(str(r[0]),0)+r[9]
    if r[0]==2026 and r[1]==last26: v26+=r[8]; s26+=r[7]
    if r[1]==last26: dt2[str(r[0])]=dt2.get(str(r[0]),0)+r[9]
seg={k:D[k] for k in ('defl','ipcm','caif','p2027_fun','seg','delitos')}
seg['seggasto']={'dev':dev,'v26':v26,'s26':s26,'dev_t2':dt2}
seg.update(lastT26=last26,lastM26=lastM26,ymin=1980)
build('site/template_seg.html',seg,'site/seguridad-caba.html')
