import re, glob, json, os
INC={'gastos en personal','bienes de consumo','servicios no personales','bienes de uso','transferencias','activos financieros','servicio de la deuda y disminución de otros pasivos','otros gastos'}
amt=re.compile(r'^(.*?)\s{2,}(-?[\d.]+)\s*$')
rows=[]; issues=[]; blk=0
for f in sorted(glob.glob('/home/claude/work/raw/p2027txt/*.txt')):
    jcode=os.path.basename(f).split(' - ')[0]
    L=open(f).read().split('\n')
    for i,l in enumerate(L):
        if 'PRESUPUESTO FINANCIERO' not in l: continue
        hdr={}
        for k in range(i-1,max(0,i-40),-1):
            m=re.match(r'^\s*(Programa|Subprograma|Proyecto|Unidad Ejecutora|Jurisdicción|Entidad|Finalidad|Función)\s*:\s*(.*)$',L[k])
            if m and m.group(1) not in hdr: hdr[m.group(1)]=m.group(2).strip()
            if 'Programa' in hdr and 'Jurisdicción' in hdr and 'Función' in hdr: 
                # stop once we've hit the Programa line (top of header)
                if re.match(r'^\s*Programa\s*:',L[k]): break
        j=i+1; cur=None; pend=''; tot=None; items=[]
        while j<len(L):
            s=L[j]
            if not s.strip() or re.match(r'^\s*(Inciso|Principal)',s) : j+=1; continue
            if s.strip().startswith('TOTAL'):
                m=re.search(r'([\d.]+)\s*$',s); tot=int(m.group(1).replace('.','')) if m else None; break
            m=amt.match(s)
            if not m:
                pend=(pend+' '+s.strip()).strip(); j+=1; continue
            name=(pend+' '+m.group(1).strip()).strip(); pend=''; v=int(m.group(2).replace('.',''))
            indent=len(s)-len(s.lstrip())
            if name.lower() in INC and indent<2: cur=name; items.append(('I',name,v))
            else: items.append(('P',name,v,cur))
            j+=1
        isum=sum(x[2] for x in items if x[0]=='I'); psum=sum(x[2] for x in items if x[0]=='P')
        if tot is None or isum!=tot or psum!=tot: issues.append((jcode,hdr.get('Programa'),tot,isum,psum))
        blk+=1
        for x in items:
            if x[0]=='P': rows.append({'blk':blk,'jcode':jcode,'jur':hdr.get('Jurisdicción',''),'ent':hdr.get('Entidad',''),'ue':hdr.get('Unidad Ejecutora',''),'prog':hdr.get('Programa',''),'fin':hdr.get('Finalidad',''),'fun':hdr.get('Función',''),'inc':x[3],'ppal':x[1],'v':x[2]})
import collections
mp=collections.defaultdict(collections.Counter)
for r in rows:
    if r['inc']: mp[r['ppal'].lower()][r['inc']]+=1
for r in rows: r['inc']=mp[r['ppal'].lower()].most_common(1)[0][0]
# dedupe aggregate blocks: within (jcode,prog), a block whose total equals the sum of the other blocks
bt=collections.Counter(); bk=collections.defaultdict(set)
for r in rows: bt[r['blk']]+=r['v']; bk[(r['jcode'],r['prog'])].add(r['blk'])
drop=set()
for k,bs in bk.items():
    if len(bs)<3: continue
    for b in bs:
        if bt[b]==sum(bt[o] for o in bs if o!=b): drop.add(b)
print('dropped aggregate blocks',len(drop))
rows=[r for r in rows if r['blk'] not in drop]
# aggregate blocks that include the detail blocks plus own spending: keep the residual
bt=collections.Counter(); bk=collections.defaultdict(set)
for r in rows: bt[r['blk']]+=r['v']; bk[(r['jcode'],r['prog'])].add(r['blk'])
for k,bs in bk.items():
    if len(bs)<3: continue
    b=max(bs,key=lambda x:bt[x]); rest=[o for o in bs if o!=b]
    if bt[b]>sum(bt[o] for o in rest) and k[0]=='40':
        sub=collections.Counter()
        for r in rows:
            if r['blk'] in rest: sub[(r['inc'],r['ppal'])]+=r['v']
        for r in rows:
            if r['blk']==b: r['v']-=sub[(r['inc'],r['ppal'])]; sub[(r['inc'],r['ppal'])]=0
        print('residual',k,bt[b]/1e6, 'leftover', sum(sub.values()))
rows=[r for r in rows if r['v']!=0]
json.dump(rows,open('/home/claude/work/p2027_prog.json','w'),ensure_ascii=False)
print('rows',len(rows),'issues',len(issues)); [print(x) for x in issues[:30]]
