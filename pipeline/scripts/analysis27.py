import json, collections, unicodedata, re
def n(s): return re.sub(r'[^a-z0-9 ]','',re.sub(r'\s+',' ',unicodedata.normalize('NFD',s).encode('ascii','ignore').decode().lower())).strip()
R=json.load(open('p2027_prog.json')); D=json.load(open('data2.json'))
P=D['P']; pd=P['dims']; O=D['O']; od=O['dims']; f26=D['defl']['p2027']['2026']
JN={'01':'Legislatura De La Ciudad De Buenos Aires','02':'Auditoria General De La Ciudad De Buenos Aires','03':'Defensoria Del Pueblo','05':'Ministerio Publico','06':'Tribunal Superior De Justicia','07':'Consejo De La Magistratura','08':'Sindicatura General De La Ciudad De Buenos Aires','09':'Procuracion General De La Ciudad','21':'Jefatura De Gabinete De Ministros','24':'Ministerio De Justicia','29':'Ministerio De Seguridad','31':'Ministerio De Movilidad E Infraestructura','35':'Ministerio De Espacio Publico E Higiene Urbana','40':'Ministerio De Salud','45':'Ministerio De Desarrollo Humano Y Hábitat','50':'Ministerio De Cultura','55':'Ministerio De Educación','60':'Ministerio De Hacienda Y Finanzas','75':'Ministerio De Desarrollo Económico','98':'Servicio De La Deuda Publica','99':'Obligaciones A Cargo Del Tesoro'}
GEN=re.compile(r'^(actividades (centrales|comunes)|conduccion|tecnica administrativa y legal|gestion de comunicacion)')
# 2027 programs (exclude amortization in 98 and activos financieros of 99 for comparability w/ Planilla 5)
def keep27(r): return not (r['jcode']=='98' and 'amortiz' in n(r['prog'])) and not (r['jcode']=='99' and r['inc']=='Activos financieros')
p27=collections.Counter(); meta={}
for r in R:
    if not keep27(r): continue
    num,_,name=r['prog'].partition(' ')
    k=(JN[r['jcode']],n(name)) if GEN.match(n(name)) else ('*',n(name))
    p27[k]+=r['v']/1e6; meta.setdefault(k,(JN[r['jcode']],name.strip(),r['fun']))
# 2026 vigente by program (T2), exclude Jefatura de Gobierno (no 2027 detail)
amort=od['inc_desc'].index('Amortización de deuda') if 'Amortización de deuda' in od['inc_desc'] else -1
p26=collections.Counter(); s26=collections.Counter(); jur26={}
for r in P['rows']:
    if r[0]!=2026 or r[1]!=2: continue
    j=pd['jur_desc'][r[2]]
    if j=='Jefatura De Gobierno' or pd['inc_desc'][r[4]]=='Amortización de deuda' or (j=='Obligaciones A Cargo Del Tesoro' and pd['inc_desc'][r[4]]=='Activos Financieros'): continue
    nm=n(pd['prog_desc'][r[3]]); k=(j,nm) if GEN.match(nm) else ('*',nm)
    p26[k]+=r[7]; s26[k]+=r[6]; jur26.setdefault(k,collections.Counter())[j]+=r[7]
# fuzzy-match renamed / truncated programs (2027 names wrap in the PDF header)
def toks(x): return set(w for w in x.split() if len(w)>3)
u27=[k for k in p27 if k not in p26]; u26=[k for k in p26 if k not in p27]
alias={}
MAN={('*','atencion medica en hospitales maternoinfantiles'):('*','atencion medica materno infantil')}
for k27 in u27:
    if k27 in MAN and MAN[k27] in p26: alias[k27]=MAN[k27]; continue
    j27=meta[k27][0]; best=None; bs=0
    for k26 in u26:
        if k26 in alias.values(): continue
        if jur26[k26].most_common(1)[0][0]!=j27 and k27[0]!='*': continue
        a,b=k27[1],k26[1]
        sc=1.0 if (b.startswith(a) or a.startswith(b)) and min(len(a),len(b))>12 else len(toks(a)&toks(b))/max(1,len(toks(a)|toks(b)))
        if sc>bs: bs,best=sc,k26
    if best and bs>=0.6: alias[k27]=best
for k27,k26 in alias.items():
    p27[k26]=p27.get(k26,0)+p27.pop(k27); meta[k26]=meta.pop(k27)
print('aliased',len(alias)); [print('  ',a[1],'<=',b[1]) for a,b in alias.items()]
progs=[]
for k in set(p26)|set(p27):
    a=p26.get(k,0)*f26; b=p27.get(k,0)
    if a<1 and b<1: continue
    j27,name27,fun=meta.get(k,(None,None,None))
    j26=jur26[k].most_common(1)[0][0] if k in jur26 else None
    n26=[pd['prog_desc'][i] for i in range(len(pd['prog_desc'])) if n(pd['prog_desc'][i])==k[1]]
    name=name27 or n26[0]
    if name27 and n26 and len(n(n26[0]))>len(n(name27))+3 and n(n26[0]).startswith(n(name27)): name=n26[0]
    progs.append({'jur':j27 or j26,'jur26':j26,'prog':name,'v26':round(p26.get(k,0),1),'s26':round(s26.get(k,0),1),'p27':round(b,1)})
print('programs',len(progs),'only26',sum(1 for p in progs if p['p27']==0),'only27',sum(1 for p in progs if p['v26']==0))
print('total v26 (2027$)',sum(p['v26'] for p in progs)*f26/1e6,'p27',sum(p['p27'] for p in progs)/1e6)
# partidas principales: 2026 vig (O cube T2, excl JG and amortization) vs 2027
pp26=collections.Counter(); pp27=collections.Counter(); ppj26=collections.Counter(); ppj27=collections.Counter(); ppinc={}
for r in O['rows']:
    if r[0]!=2026 or r[1]!=2: continue
    j=od['jur_desc'][r[2]]
    if j=='Jefatura De Gobierno' or r[3]==amort or (j=='Obligaciones A Cargo Del Tesoro' and od['inc_desc'][r[3]]=='Activos Financieros'): continue
    k=n(od['ppal_desc'][r[4]]); pp26[k]+=r[8]; ppj26[(j,k)]+=r[8]; ppinc.setdefault(k,(od['inc_desc'][r[3]],od['ppal_desc'][r[4]]))
for r in R:
    if not keep27(r): continue
    k=n(r['ppal']); pp27[k]+=r['v']/1e6; ppj27[(JN[r['jcode']],k)]+=r['v']/1e6; ppinc.setdefault(k,(r['inc'],r['ppal']))
print('pp tot',sum(pp26.values())*f26/1e6,sum(pp27.values())/1e6)
miss=[k for k in pp27 if k not in pp26]; print('ppal only 2027',miss[:20]); print('only 2026',[k for k in pp26 if k not in pp27][:20])
partidas=[{'inc':ppinc[k][0],'ppal':ppinc[k][1],'v26':round(pp26.get(k,0),1),'p27':round(pp27.get(k,0),1)} for k in set(pp26)|set(pp27)]
pj=[{'jur':j,'ppal':ppinc[k][1],'inc':ppinc[k][0],'v26':round(ppj26.get((j,k),0),1),'p27':round(ppj27.get((j,k),0),1)} for (j,k) in set(ppj26)|set(ppj27)]
json.dump({'progs':progs,'partidas':partidas,'ppj':pj,'f26':f26},open('analysis27.json','w'),ensure_ascii=False)
