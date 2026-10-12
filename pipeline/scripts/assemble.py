import json,glob,re,base64,gzip,os
T='/root/.claude/projects/-home-claude/4300654a-61f3-5d7d-9a91-7d488cb58759/tool-results/'
chunks={}
for f in glob.glob(T+'mcp-remote-devices-Claude_Browser__javascript_tool-*.txt'):
    try: d=json.load(open(f))
    except: continue
    t=''.join(x['text'] for x in d if x['type']=='text')
    m=re.match(r'"?CHUNK(\d+)\|B64START(.*?)B64END',t,re.S)
    if m: chunks[int(m.group(1))]=m.group(2)
print(sorted(chunks)==list(range(35)), len(chunks))
big=''.join(chunks[i] for i in range(35)).replace('\\n','\n')
os.makedirs('raw/gasto',exist_ok=True)
for line in big.split('\n'):
    name,b64=line.split('::')
    raw=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
    open('raw/gasto/'+name.replace('.csv','.txt'),'w').write(raw)
    meta,csv=raw.split('\n@@\n')
    m=json.loads(meta)
    print(name, m['n'], m['bad'], csv.count('\n'), csv.split('\n')[0])
