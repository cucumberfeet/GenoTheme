import random
exec(open('text.py').read().split('# B: System log')[0].replace("save(o,'genotheme-manifesto')",""))
# spine from eye
o.append(f'<polyline points="320,100 320,40 380,40" fill="none" stroke="{C}" stroke-width="2" opacity=".7"/>')
o.append(f'<line x1="305" y1="40" x2="305" y2="1100" stroke="{B}" stroke-width="1" opacity=".4"/>')
o.append(f'<text transform="translate(296,760) rotate(-90)" font-family="IBM Plex Mono" font-size="12" fill="{M}" letter-spacing="4">PROPERTY OF GENOCORP SOLUTIONS INC.</text>')
# warning block (from lines), top right
o.append('<g transform="translate(1550,-1170)">')
o.append(f'<polygon points="300,1340 340,1270 380,1340" fill="none" stroke="{R}" stroke-width="3" filter="url(#gl)"/><rect x="337" y="1292" width="6" height="26" fill="{R}"/><rect x="337" y="1324" width="6" height="7" fill="{R}"/>')
random.seed(7)
o.append(f'<g fill="{R}" opacity=".85">'+''.join(f'<rect x="410" y="{1290+i*10}" width="{w}" height="4"/>' for i,w in enumerate([40,26,34,26,34]))+'</g>')
t(o,470,1300,"UNAUTHORIZED ACCESS IS A CRIME",R,12,extra='opacity=".8"')
t(o,470,1318,"AGAINST THE SHAREHOLDERS",R,12,extra='opacity=".8"')
t(o,470,1336,"REF 0xG3N0-C0RP-1101",M,12)
t(o,740,1318,"STATUS: OPERATIONAL",B,12,extra='opacity=".7"'); o.append(f'<polygon points="900,1308 930,1314 900,1320" fill="{B}"/>')
o.append('</g>')
# terminal (from eye), under it
o.append('<g transform="translate(1590,180)">')
tx,ty,tw,th=330,90,560,190
o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="#05061a" fill-opacity=".6" stroke="{B}" stroke-width="1.5"/>')
o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="26" fill="{B}" opacity=".85"/>'); t(o,tx+12,ty+18,"GENOCORP TRUST NETWORK // TTY0","#020205",13,w=700)
o.append(''.join(f'<rect x="{tx+tw-20-i*16}" y="{ty+8}" width="10" height="10" fill="{R if i==0 else "#020205"}"/>' for i in range(3)))
for i,(l,st) in enumerate([("> handshake ........................ ","OK"),("> biometric sync ................... ","OK"),("> loyalty audit ..................... ","PASS"),("> free will module .................. ","DISABLED")]):
  t(o,tx+16,ty+56+i*24,l,M,13); t(o,tx+tw-16,ty+56+i*24,st,R if st=="DISABLED" else B,13,"end",700)
t(o,tx+16,ty+th-16,"citizen@bartholomew:~$",C,13,w=700); o.append(f'<rect x="{tx+219}" y="{ty+th-29}" width="9" height="16" fill="{R}"/>')
o.append('</g>')
save(o,'genotheme-manifesto')
