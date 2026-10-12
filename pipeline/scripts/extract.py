import json,sys,base64,re
src,dst=sys.argv[1],sys.argv[2]
d=json.load(open(src))
t=''.join(x['text'] for x in d if x['type']=='text')
m=re.search(r'B64START(.*?)B64END',t,re.S)
s=m.group(1).replace('\\n','')
open(dst,'wb').write(base64.b64decode(s))
print(dst, len(base64.b64decode(s)))
