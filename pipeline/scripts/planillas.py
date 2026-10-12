import json,re
d=json.load(open('raw/planillas2027_items.json'))
num=lambda s: re.match(r'^-?[\d\.]+$',s) and ('.' in s or s=='0' or s.isdigit())
def tonum(s): return float(s.replace('.',''))
def parse_rot(p, header_x=(120,145), row_ymax=25):
    items=d[str(p)]
    hdr=[i for i in items if header_x[0]<=i[5]<=header_x[1] and not num(i[0])]
    # merge header pieces by center y
    cols=[]
    for h in sorted(hdr,key=lambda i:i[6]+i[7]/2):
        c=h[6]+h[7]/2
        if cols and abs(cols[-1][1]-c)<15: cols[-1]=(cols[-1][0]+' '+h[0], (cols[-1][1]+c)/2)
        else: cols.append((h[0],c))
    rows=[(i[0],i[5]) for i in items if i[6]<row_ymax and not num(i[0])]
    data={}
    for i in items:
        if not num(i[0]) or i[5]<145: continue
        yc=i[6]+i[7]/2
        col=min(cols,key=lambda c:abs(c[1]-yc))
        row=min(rows,key=lambda r:abs(r[1]-i[5]))
        if abs(row[1]-i[5])>6: continue
        data.setdefault(row[0],{})[col[0]]=tonum(i[0])
    return cols,rows,data
if __name__=='__main__':
    cols,rows,data=parse_rot(5)
    print([c[0] for c in cols])
    for r,v in data.items():
        tot=v.get('TOTAL GENERAL',0); s=sum(x for k,x in v.items() if k!='TOTAL GENERAL')
        print(r[:40].ljust(40), round(tot/1e9,1), round(s/1e9,1))
