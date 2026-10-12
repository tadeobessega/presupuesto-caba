import base64
t=open('template.html').read()
t=t.replace('{{LOGO_NEG}}',base64.b64encode(open('assets/logo_negativo.png','rb').read()).decode())
t=t.replace('{{LOGO_POS}}',base64.b64encode(open('assets/logo_positivo.png','rb').read()).decode())
t=t.replace('{{DATA}}',open('data.json').read().replace('</','<\\/'))
t=t.replace('{{APP}}',open('app.js').read())
open('/home/claude/out/presupuesto-porteno-2027.html','w').write(t)
print(len(t)/1e6,'MB')
