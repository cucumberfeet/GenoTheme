import random, cairosvg
random.seed(7)
W,H=2560,1440
R="#ff0000"; B="#4d6bff"; C="#9fb3ff"; M="#6a7095"; BG="#020205"
o=[]
a=o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#080a24"/><stop offset=".55" stop-color="#04040f"/><stop offset="1" stop-color="#020205"/></linearGradient>'
  '<radialGradient id="r" cx=".12" cy=".05" r=".7"><stop offset="0" stop-color="#1a2580" stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
  '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
a(f'<rect width="{W}" height="{H}" fill="url(#g)"/><rect width="{W}" height="{H}" fill="url(#r)"/>')
# scanlines
a('<g opacity=".05">'+''.join(f'<rect y="{y}" width="{W}" height="1" fill="{B}"/>' for y in range(0,H,4))+'</g>')
# dot matrix fields (left side, fading)
def dots(x0,y0,w,h,step,col,op,dens):
    s=[]
    for y in range(y0,y0+h,step):
        for x in range(x0,x0+w,step):
            if random.random()<dens*(1-(x-x0)/w):
                s.append(f'<rect x="{x}" y="{y}" width="2" height="2"/>')
    a(f'<g fill="{col}" opacity="{op}">'+''.join(s)+'</g>')
dots(60,300,420,520,9,B,.35,.55)
dots(60,1000,600,380,9,B,.3,.5)
dots(1100,250,500,180,9,B,.18,.35)
# spine (blue main line)
sp=[(250,0),(250,330),(205,375),(205,820),(165,860),(165,1080),(205,1120),(205,H)]
pts=" ".join(f"{x},{y}" for x,y in sp)
a(f'<polyline points="{pts}" fill="none" stroke="{B}" stroke-width="3" filter="url(#glow)"/>')
a(f'<polyline points="{" ".join(f"{x+14},{y}" for x,y in sp)}" fill="none" stroke="{B}" stroke-width="1" opacity=".35"/>')
# side bracket
a(f'<polyline points="205,860 185,880 185,1060 205,1080" fill="none" stroke="{R}" stroke-width="2" opacity=".8"/>')
# top lines
a(f'<polyline points="250,250 360,160 1420,160 1690,430 2290,430" fill="none" stroke="{B}" stroke-width="2.5" filter="url(#glow)"/>')
a(f'<polyline points="1185,140 1240,95 1780,95 2010,0" fill="none" stroke="{B}" stroke-width="1.5" opacity=".5"/>')
a(f'<polyline points="2290,430 2560,160" fill="none" stroke="{B}" stroke-width="2.5" filter="url(#glow)"/>')
# red accent line on top
a(f'<polyline points="1420,175 1680,445 1700,445" fill="none" stroke="{R}" stroke-width="2" opacity=".85"/>')
# label block top-right
a(f'<polygon points="1680,430 2290,430 2255,465 1720,465" fill="{R}" opacity=".9"/>')
a(f'<polygon points="2030,404 2280,404 2290,430 2010,430" fill="none" stroke="{C}" stroke-width="1.5"/>')
a(''.join(f'<line x1="{2040+i*9}" y1="410" x2="{2034+i*9}" y2="424" stroke="{C}" stroke-width="3"/>' for i in range(10)))
a(f'<text x="2245" y="456" font-family="Orbitron" font-weight="800" font-size="26" fill="#020205" text-anchor="end" letter-spacing="4">GENOCORP</text>')
a(f'<text x="1735" y="455" font-family="IBM Plex Mono" font-weight="700" font-size="15" fill="#020205">// SECTOR 09 // TRUST NETWORK</text>')
a(f'<text x="2280" y="495" font-family="IBM Plex Mono" font-size="13" fill="{M}" text-anchor="end">GENOCORP SOLUTIONS INC. // NODE BALTHASAR // UPLINK STABLE // 0x6E9A2B</text>')
a(f'<text x="2280" y="515" font-family="IBM Plex Mono" font-size="13" fill="{M}" text-anchor="end">ALL CITIZENS ARE MONITORED FOR THEIR OWN SAFETY  —  COMPLIANCE IS FREEDOM</text>')
a(''.join(f'<rect x="{2240+i*16}" y="{525}" width="10" height="6" fill="{R}"/>' for i in range(3)))
# barcode block near top-left (right of dock)
x=280
bc=[]
y=20
while y<300:
    h=random.choice([2,3,4,6,8,12]); 
    if random.random()<.75: bc.append(f'<rect x="{x}" y="{y}" width="{random.choice([40,52,60,60])}" height="{h}"/>')
    y+=h+random.choice([2,3,4])
a(f'<g fill="{C}" opacity=".9">'+''.join(bc)+'</g>')
a(f'<rect x="{x}" y="305" width="60" height="26" fill="{C}"/><text x="{x+30}" y="323" font-family="IBM Plex Mono" font-weight="700" font-size="13" fill="#020205" text-anchor="middle">GC-01</text>')
for i,yy in enumerate([348,378]):
    a(f'<g stroke="{C}" stroke-width="1.5" fill="none"><rect x="{x+20}" y="{yy}" width="18" height="18"/><line x1="{x+20}" y1="{yy}" x2="{x+38}" y2="{yy+18}"/><line x1="{x+38}" y1="{yy}" x2="{x+20}" y2="{yy+18}"/></g>')
# small vertical text on spine
a(f'<text transform="translate(232,700) rotate(-90)" font-family="IBM Plex Mono" font-size="12" fill="{M}" letter-spacing="3">GENO//CORP  SYS.SPINE  v2.6</text>')
# bottom-left warning
a(f'<polygon points="300,1340 340,1270 380,1340" fill="none" stroke="{R}" stroke-width="3" filter="url(#glow)"/><rect x="337" y="1292" width="6" height="26" fill="{R}"/><rect x="337" y="1324" width="6" height="7" fill="{R}"/>')
a(f'<g fill="{R}" opacity=".85">'+''.join(f'<rect x="{410}" y="{1290+i*10}" width="{random.choice([26,34,40])}" height="4"/>' for i in range(5))+'</g>')
a(f'<text x="470" y="1300" font-family="IBM Plex Mono" font-size="12" fill="{R}" opacity=".8">UNAUTHORIZED ACCESS IS A CRIME</text>')
a(f'<text x="470" y="1318" font-family="IBM Plex Mono" font-size="12" fill="{R}" opacity=".8">AGAINST THE SHAREHOLDERS</text>')
a(f'<text x="470" y="1336" font-family="IBM Plex Mono" font-size="12" fill="{M}">REF 0xG3N0-C0RP-1101</text>')
a(f'<text x="740" y="1318" font-family="IBM Plex Mono" font-size="12" fill="{B}" opacity=".7">STATUS: OPERATIONAL</text><polygon points="900,1308 930,1314 900,1320" fill="{B}"/>')
a('</svg>')
open('genotheme-wallpaper.svg','w').write("\n".join(o))
cairosvg.svg2png(url='genotheme-wallpaper.svg',write_to='genotheme-3840x2160.png',output_width=3840,output_height=2160)
cairosvg.svg2png(url='genotheme-wallpaper.svg',write_to='preview.png',output_width=1600,output_height=900)
