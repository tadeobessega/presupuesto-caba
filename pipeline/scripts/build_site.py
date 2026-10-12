import json
D=json.load(open('data2.json'))
neg=D.pop('logo_neg'); pos=D.pop('logo_pos')
t=open('site/template.html').read()
s=json.dumps(D,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
t=t.replace('__LOGO_NEG__',neg).replace('__LOGO_POS__',pos).replace('__DATA__',s)
open('site/presupuesto-caba-2027.html','w').write(t)
import os; print(os.path.getsize('site/presupuesto-caba-2027.html')/1e6)
