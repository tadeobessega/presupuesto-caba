import json,re
d=json.load(open('raw/planillas2026_items.json'))
isnum=lambda s: bool(re.match(r'^-?[\d\.]+$',s))
tonum=lambda s: float(s.replace('.',''))
def parse_land(p, hdr_y=(445,470), lab_x=30):
    items=d[str(p)]
    hdr=[i for i in items if hdr_y[0]<=i[6]<=hdr_y[1] and not isnum(i[0]) and i[5]>100]
    cols=[]
    for h in sorted(hdr,key=lambda i:i[5]+i[7]/2):
        c=h[5]+h[7]/2
        if cols and abs(cols[-1][1]-c)<18: cols[-1]=(cols[-1][0]+' '+h[0] if h[6]<cols[-1][2] else h[0]+' '+cols[-1][0], (cols[-1][1]+c)/2, min(h[6],cols[-1][2]))
        else: cols.append((h[0],c,h[6]))
    labs=sorted([i for i in items if i[5]<lab_x and not isnum(i[0]) and i[6]<hdr_y[0]],key=lambda i:-i[6])
    rows=[]
    for l in labs:
        if l[5]>20 and rows: rows[-1]=(rows[-1][0]+' '+l[0],rows[-1][1]); continue
        rows.append((l[0],l[6]))
    data={}
    for i in items:
        if not isnum(i[0]) or i[6]>=hdr_y[0]: continue
        xe=i[5]+i[7]
        col=min(cols,key=lambda c:abs(c[1]-(i[5]+i[7]/2)))
        row=min(rows,key=lambda r:abs(r[1]-i[6]))
        if abs(row[1]-i[6])>5: continue
        data.setdefault(row[0],{})[col[0]]=tonum(i[0])
    return cols,data
out={}
for name,p in [('jur_inc',5),('fun_inc',4)]:
    cols,data=parse_land(p); out[name]=data
    print([c[0] for c in cols])
    for k,v in data.items():
        tg=[x for kk,x in v.items() if 'TOTAL' in kk]; tot=tg[0] if tg else 0
        print(' ',k[:40].ljust(40), round(tot/1e9,1), round(sum(x for kk,x in v.items() if 'TOTAL' not in kk)/1e9,1))
json.dump(out,open('p2026.json','w'),ensure_ascii=False)
