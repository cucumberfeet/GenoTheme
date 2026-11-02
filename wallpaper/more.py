import random, math, cairosvg
W,H=2560,1440
R="#ff0000"; B="#4d6bff"; C="#9fb3ff"; M="#6a7095"; K="#020205"
def base(seed, cx=.5, cy=.35):
  random.seed(seed); o=[]
  o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
  o.append(f'<defs><radialGradient id="g" cx="{cx}" cy="{cy}" r=".85"><stop offset="0" stop-color="#0b1038"/><stop offset=".5" stop-color="#05061a"/><stop offset="1" stop-color="{K}"/></radialGradient>'
   '<filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
  o.append(f'<rect width="{W}" height="{H}" fill="url(#g)"/>')
  o.append('<g opacity=".045">'+''.join(f'<rect y="{y}" width="{W}" height="1" fill="{B}"/>' for y in range(0,H,4))+'</g>')
  return o
def t(o,x,y,s,col=M,size=13,anchor="start",w=400,ls=1,extra=""):
  o.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Mono" font-weight="{w}" font-size="{size}" fill="{col}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{s}</text>')
def save(o,name):
  o.append('</svg>'); open(name+'.svg','w').write("\n".join(o))
  cairosvg.svg2png(url=name+'.svg',write_to=name+'-3840x2160.png',output_width=3840,output_height=2160)
  cairosvg.svg2png(url=name+'.svg',write_to=name+'-preview.png',output_width=1280,output_height=720)

# 3: Skyline line-art
o=base(3,.45,.45)
o.append(f'<circle cx="1250" cy="430" r="230" fill="none" stroke="{R}" stroke-width="3" filter="url(#gl)"/>')
o.append('<g stroke="%s" stroke-width="1" opacity=".25">'%R+''.join(f'<line x1="{1250-math.sqrt(max(0,230**2-(y-430)**2)):.0f}" y1="{y}" x2="{1250+math.sqrt(max(0,230**2-(y-430)**2)):.0f}" y2="{y}"/>' for y in range(470,660,14))+'</g>')
x=330; bl=[]
while x<1900:
  w=random.randint(50,140); h=random.randint(180,620)
  if 1150<x<1350: h=random.randint(700,820)
  bl.append((x,w,h)); x+=w+random.randint(0,18)
ground=1180
for (x,w,h) in bl:
  top=ground-h
  op=max(.25,1-(x-330)/2200)
  o.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{K}" fill-opacity=".85" stroke="{B}" stroke-width="1.5" opacity="{op:.2f}"/>')
  for yy in range(top+20,ground-10,26):
    for xx in range(x+10,x+w-10,18):
      if random.random()<.18: o.append(f'<rect x="{xx}" y="{yy}" width="6" height="3" fill="{C if random.random()<.9 else R}" opacity="{op*.8:.2f}"/>')
  if random.random()<.3: o.append(f'<line x1="{x+w/2}" y1="{top}" x2="{x+w/2}" y2="{top-50}" stroke="{B}" stroke-width="1.5" opacity="{op:.2f}"/><circle cx="{x+w/2}" cy="{top-52}" r="3" fill="{R}"/>')
o.append(f'<line x1="300" y1="{ground}" x2="2000" y2="{ground}" stroke="{C}" stroke-width="1.5" opacity=".6"/>')
o.append('<g stroke="%s" stroke-width="1" opacity=".2">'%B+''.join(f'<line x1="{1150+(i-12)*60}" y1="{ground}" x2="{1150+(i-12)*240}" y2="{H}"/>' for i in range(25))+''.join(f'<line x1="300" y1="{ground+d}" x2="2000" y2="{ground+d}"/>' for d in [12,30,58,100,170])+'</g>')
t(o,340,110,"NIGHT CITY MUNICIPAL GRID // OWNED BY GENOCORP",C,15,w=700,ls=4)
t(o,340,134,"SECTOR 09 — POPULATION 4,221,907 — HAPPINESS QUOTA MET",M,13)
o.append(f'<rect x="340" y="150" width="240" height="4" fill="{R}"/>')
save(o,'genotheme-skyline')

# 4: Data wall + banner
o=base(4,.6,.3)
cols=[]
for c in range(0,60):
  x=330+c*38
  if random.random()<.55:
    y0=random.randint(-200,500); n=random.randint(10,40)
    for i in range(n):
      op=.5*(1-i/n)
      cols.append(f'<text x="{x}" y="{y0+i*22}" opacity="{op:.2f}">{random.choice("0123456789ABCDEF")}{random.choice("0123456789ABCDEF")}</text>')
o.append(f'<g font-family="IBM Plex Mono" font-size="14" fill="{B}">'+''.join(cols)+'</g>')
o.append(f'<polygon points="330,600 2560,470 2560,610 330,740" fill="{R}" opacity=".92"/>')
o.append(f'<polygon points="330,760 2560,630 2560,640 330,770" fill="{B}" opacity=".8"/>')
o.append(f'<text font-family="Orbitron" font-weight="800" font-size="96" fill="{K}" letter-spacing="22" transform="translate(420,705) rotate(-3.34)">GENOCORP</text>')
o.append(f'<text font-family="IBM Plex Mono" font-weight="700" font-size="22" fill="{K}" letter-spacing="6" transform="translate(1500,640) rotate(-3.34)">// COMPLIANCE IS FREEDOM //</text>')
t(o,345,830,"SYS.MSG 0x1101: YOUR PRODUCTIVITY HAS BEEN NOTED.",C,14,w=700,ls=2)
t(o,345,852,"PLEASE CONTINUE BEING AN ASSET.",M,13,ls=2)
for (x,y,dx,dy) in [(320,40,1,1),(320,1100,1,-1)]:
  o.append(f'<polyline points="{x},{y+60*dy} {x},{y} {x+60*dx},{y}" fill="none" stroke="{C}" stroke-width="2" opacity=".7"/>')
save(o,'genotheme-banner')

# 5: Tower schematic
o=base(5,.55,.4)
gx=[]
for x in range(320,W,64): gx.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
for y in range(0,H,64): gx.append(f'<line x1="320" y1="{y}" x2="{W}" y2="{y}"/>')
o.append(f'<g stroke="{B}" stroke-width="1" opacity=".07">'+''.join(gx)+'</g>')
cx=1350; base_y=1150; levels=[(420,0),(360,160),(300,320),(230,500),(160,680),(90,840),(30,980)]
pts=[]
for i,(hw,h) in enumerate(levels):
  y=base_y-h
  o.append(f'<line x1="{cx-hw}" y1="{y}" x2="{cx+hw}" y2="{y}" stroke="{B}" stroke-width="2" filter="url(#gl)"/>')
  if i+1<len(levels):
    hw2,h2=levels[i+1]; y2=base_y-h2
    o.append(f'<polyline points="{cx-hw},{y} {cx-hw2},{y2}" fill="none" stroke="{B}" stroke-width="2" filter="url(#gl)"/><polyline points="{cx+hw},{y} {cx+hw2},{y2}" fill="none" stroke="{B}" stroke-width="2" filter="url(#gl)"/>')
    o.append(f'<line x1="{cx-hw}" y1="{y}" x2="{cx+hw2}" y2="{y2}" stroke="{B}" stroke-width="1" opacity=".3"/><line x1="{cx+hw}" y1="{y}" x2="{cx-hw2}" y2="{y2}" stroke="{B}" stroke-width="1" opacity=".3"/>')
o.append(f'<line x1="{cx}" y1="{base_y-980}" x2="{cx}" y2="{base_y-1080}" stroke="{C}" stroke-width="2"/><circle cx="{cx}" cy="{base_y-1084}" r="6" fill="{R}" filter="url(#gl)"/>')
o.append(f'<polygon points="{cx},{base_y-740} {cx+70},{base_y-620} {cx-70},{base_y-620}" fill="none" stroke="{R}" stroke-width="4" filter="url(#gl)"/>')
o.append(f'<line x1="{cx-520}" y1="{base_y}" x2="{cx+520}" y2="{base_y}" stroke="{C}" stroke-width="1.5"/>')
# dimension line
dx=cx+560
o.append(f'<g stroke="{C}" stroke-width="1" opacity=".7"><line x1="{dx}" y1="{base_y}" x2="{dx}" y2="{base_y-1084}"/><line x1="{dx-10}" y1="{base_y}" x2="{dx+10}" y2="{base_y}"/><line x1="{dx-10}" y1="{base_y-1084}" x2="{dx+10}" y2="{base_y-1084}"/></g>')
t(o,dx+18,base_y-540,"H = 2,077 M",C,14,w=700,ls=2)
calls=[(4,"LVL 180 // EXECUTIVE SUITES","ACCESS: CLASS A ONLY"),(2,"LVL 090 // DATA VAULT","ZERO-KNOWLEDGE STORAGE"),(0,"LVL 000 // CITIZEN INTAKE","PLEASE HAVE BIOMETRICS READY")]
for i,(lv,a1,a2) in enumerate(calls):
  hw,h=levels[lv]; y=base_y-h
  lx=cx-hw-40; tx=480
  o.append(f'<polyline points="{cx-hw},{y} {lx},{y-30} {tx+330},{y-30}" fill="none" stroke="{R if i==0 else C}" stroke-width="1" opacity=".8"/>')
  t(o,tx,y-36,a1,R if i==0 else C,14,w=700,ls=2); t(o,tx,y-16,a2,M,12)
t(o,340,90,"DWG NO. GC-HQ-0001 // REV 7",C,14,w=700,ls=3)
t(o,340,112,"GENOCORP ARCOLOGY — STRUCTURAL OVERVIEW — CONFIDENTIAL",M,12)
o.append(f'<rect x="340" y="124" width="200" height="3" fill="{R}"/>')
save(o,'genotheme-schematic')
