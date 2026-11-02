import random, math, cairosvg
random.seed(11)
W,H=2560,1440
R="#ff0000"; B="#4d6bff"; C="#9fb3ff"; M="#6a7095"
o=[];a=o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><radialGradient id="g" cx=".58" cy=".36" r=".8"><stop offset="0" stop-color="#0b1038"/><stop offset=".5" stop-color="#05061a"/><stop offset="1" stop-color="#020205"/></radialGradient>'
  '<filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
a(f'<rect width="{W}" height="{H}" fill="url(#g)"/>')
a('<g opacity=".045">'+''.join(f'<rect y="{y}" width="{W}" height="1" fill="{B}"/>' for y in range(0,H,4))+'</g>')
# faint hex grid upper right
hx=[]
s=26
for r_ in range(0,16):
  for c_ in range(0,22):
    x=1700+c_*s*1.5; y=40+r_*s*1.732+(c_%2)*s*.866
    d=math.hypot(x-2300,y-150)
    if d<620 and random.random()<.8:
      p=" ".join(f"{x+s*.55*math.cos(math.radians(60*k)):.1f},{y+s*.55*math.sin(math.radians(60*k)):.1f}" for k in range(6))
      hx.append(f'<polygon points="{p}" opacity="{max(0.02,.16-d/4000):.2f}"/>')
a(f'<g fill="none" stroke="{B}" stroke-width="1">'+''.join(hx)+'</g>')
cx,cy=1460,560
def arc(r,a0,a1,col,w,op=1,f=False):
  x0,y0=cx+r*math.cos(math.radians(a0)),cy+r*math.sin(math.radians(a0))
  x1,y1=cx+r*math.cos(math.radians(a1)),cy+r*math.sin(math.radians(a1))
  la=1 if (a1-a0)%360>180 else 0
  a(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {la} 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" opacity="{op}" {"filter=\"url(#gl)\"" if f else ""}/>')
# crosshair lines
a(f'<g stroke="{B}" stroke-width="1" opacity=".35"><line x1="360" y1="{cy}" x2="{cx-420}" y2="{cy}"/><line x1="{cx+420}" y1="{cy}" x2="{W}" y2="{cy}"/><line x1="{cx}" y1="0" x2="{cx}" y2="{cy-420}"/><line x1="{cx}" y1="{cy+420}" x2="{cx}" y2="1100"/></g>')
# rings
arc(380,200,340,B,2.5,1,True); arc(380,20,160,B,2.5,1,True)
arc(395,-35,-5,R,6,.95,True); arc(395,150,158,R,6,.9)
arc(340,0,359.9,B,1,.3)
arc(300,100,250,C,1.5,.7); arc(300,280,60,C,1.5,.7)
arc(250,0,359.9,B,14,.12)
# ticks
for k in range(120):
  ang=math.radians(k*3); l=18 if k%10==0 else 8
  r1=355; r2=r1+l
  a(f'<line x1="{cx+r1*math.cos(ang):.1f}" y1="{cy+r1*math.sin(ang):.1f}" x2="{cx+r2*math.cos(ang):.1f}" y2="{cy+r2*math.sin(ang):.1f}" stroke="{C}" stroke-width="1.2" opacity="{.8 if k%10==0 else .35}"/>')
# central emblem: eye / triangle
a(f'<polygon points="{cx},{cy-150} {cx+130},{cy+75} {cx-130},{cy+75}" fill="none" stroke="{R}" stroke-width="4" filter="url(#gl)"/>')
a(f'<polygon points="{cx},{cy-95} {cx+82},{cy+47} {cx-82},{cy+47}" fill="none" stroke="{R}" stroke-width="1.5" opacity=".6"/>')
a(f'<path d="M{cx-70},{cy+10} Q{cx},{cy-45} {cx+70},{cy+10} Q{cx},{cy+60} {cx-70},{cy+10} Z" fill="none" stroke="{C}" stroke-width="2"/>')
a(f'<circle cx="{cx}" cy="{cy+10}" r="18" fill="{R}" filter="url(#gl)"/><circle cx="{cx}" cy="{cy+10}" r="6" fill="#020205"/>')
# ring labels
def t(x,y,s,col=M,size=13,anchor="start",w=400,ls=1):
  a(f'<text x="{x}" y="{y}" font-family="IBM Plex Mono" font-weight="{w}" font-size="{size}" fill="{col}" text-anchor="{anchor}" letter-spacing="{ls}">{s}</text>')
t(cx+300,cy-330,"OBSERVATION LOOP 07",C,14,w=700,ls=3); t(cx+300,cy-312,"SUBJECT: CUCUMBERFEET // TRUST INDEX 99.7%")
a(f'<polyline points="{cx+250},{cy-290} {cx+290},{cy-325} {cx+640},{cy-325}" fill="none" stroke="{C}" stroke-width="1" opacity=".7"/>')
t(cx-300,cy+350,"THREAT LEVEL",R,13,"end",700,3); t(cx-300,cy+368,"NOMINAL // NO DISSENT DETECTED",M,13,"end")
a(f'<polyline points="{cx-260},{cy+300} {cx-290},{cy+340} {cx-640},{cy+340}" fill="none" stroke="{R}" stroke-width="1" opacity=".7"/>')
# wordmark under ring
a(f'<text x="{cx}" y="{cy+470}" font-family="Orbitron" font-weight="800" font-size="40" fill="{C}" text-anchor="middle" letter-spacing="18">GENOCORP</text>')
t(cx,cy+500,"WE SEE YOU. WE CARE.",M,14,"middle",400,8)
# terminal window top-left (right of dock)
tx,ty,tw,th=330,90,560,190
a(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="#05061a" fill-opacity=".6" stroke="{B}" stroke-width="1.5"/>')
a(f'<rect x="{tx}" y="{ty}" width="{tw}" height="26" fill="{B}" opacity=".85"/>'); t(tx+12,ty+18,"GENOCORP TRUST NETWORK // TTY0","#020205",13,w=700)
a(''.join(f'<rect x="{tx+tw-20-i*16}" y="{ty+8}" width="10" height="10" fill="{R if i==0 else "#020205"}"/>' for i in range(3)))
lines=[("> handshake ........................ ",C,"OK"),("> biometric sync ................... ",C,"OK"),("> loyalty audit ..................... ",C,"PASS"),("> free will module .................. ",C,"DISABLED")]
for i,(l,col,st) in enumerate(lines):
  t(tx+16,ty+56+i*24,l,M,13); t(tx+tw-16,ty+56+i*24,st,R if st=="DISABLED" else B,13,"end",700)
t(tx+16,ty+th-16,"citizen@balthasar:~$",C,13,w=700); a(f'<rect x="{tx+190}" y="{ty+th-29}" width="9" height="16" fill="{R}"/>')
# bottom-left meters
mx,my=340,1180
for i in range(14):
  h=random.randint(20,130)
  a(f'<rect x="{mx+i*16}" y="{my+140-h}" width="9" height="{h}" fill="{R if h>115 else B}" opacity="{.9 if h>115 else .6}"/>')
a(f'<line x1="{mx-6}" y1="{my+146}" x2="{mx+230}" y2="{my+146}" stroke="{C}" stroke-width="1"/>')
t(mx,my+168,"NEURAL LOAD // SECTOR 09",M,12)
# corner brackets of main area
for (x,y,dx,dy) in [(320,40,1,1),(2520,40,-1,1)]:
  a(f'<polyline points="{x},{y+60*dy} {x},{y} {x+60*dx},{y}" fill="none" stroke="{C}" stroke-width="2" opacity=".7"/>')
# left thin vertical rail
a(f'<line x1="305" y1="40" x2="305" y2="1100" stroke="{B}" stroke-width="1" opacity=".4"/>')
a(f'<text transform="translate(296,760) rotate(-90)" font-family="IBM Plex Mono" font-size="12" fill="{M}" letter-spacing="4">PROPERTY OF GENOCORP SOLUTIONS INC.</text>')
a('</svg>')
open('genotheme-wallpaper-2.svg','w').write("\n".join(o))
cairosvg.svg2png(url='genotheme-wallpaper-2.svg',write_to='genotheme-2-3840x2160.png',output_width=3840,output_height=2160)
cairosvg.svg2png(url='genotheme-wallpaper-2.svg',write_to='preview2.png',output_width=1600,output_height=900)
