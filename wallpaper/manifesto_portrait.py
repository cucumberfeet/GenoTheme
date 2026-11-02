# GenoTheme Manifesto — portrait edition for Balthasar's DP-2 (864x1536 logical @1.25 = 1080x1920).
# Canvas is in logical pixels (1 unit = 1 logical px, same as the 2560x1440 landscape canvas),
# rendered at 2160x3840 (2x the physical panel) so text matches the landscape wallpaper's size.
# DP-2 has no panels or widgets, so the whole screen is usable; margins kept for the folder view.
import random, textwrap, cairosvg
exec(open('more.py').read().split('# 3: Skyline')[0])          # palette, base(), t()
W,H=864,1536
def big(o,x,y,s,size,col,fam="Oswald",w=700,ls=4,outline=False,anchor="start",op=1):
  paint=f'fill="none" stroke="{col}" stroke-width="2"' if outline else f'fill="{col}"'
  o.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-weight="{w}" font-size="{size}" {paint} letter-spacing="{ls}" text-anchor="{anchor}" opacity="{op}">{s}</text>')
def nb(s): return s.replace(" ","&#160;")

o=base(21,.3,.35)
X=92; RX=824                                    # text column (spine sits at x=48)
# --- left spine (from the eye design)
o.append(f'<polyline points="64,96 64,40 124,40" fill="none" stroke="{C}" stroke-width="2" opacity=".7"/>')
o.append(f'<line x1="48" y1="40" x2="48" y2="1490" stroke="{B}" stroke-width="1" opacity=".4"/>')
o.append(f'<text transform="translate(39,1000) rotate(-90)" font-family="IBM Plex Mono" font-size="12" fill="{M}" letter-spacing="4">PROPERTY OF GENOCORP SOLUTIONS INC.</text>')
# --- warning block (from the lines design), top
o.append('<g transform="translate(-208,-1196)">')
o.append(f'<polygon points="300,1340 340,1270 380,1340" fill="none" stroke="{R}" stroke-width="3" filter="url(#gl)"/><rect x="337" y="1292" width="6" height="26" fill="{R}"/><rect x="337" y="1324" width="6" height="7" fill="{R}"/>')
o.append(f'<g fill="{R}" opacity=".85">'+''.join(f'<rect x="410" y="{1290+i*10}" width="{w}" height="4"/>' for i,w in enumerate([40,26,34,26,34]))+'</g>')
t(o,470,1300,"UNAUTHORIZED ACCESS IS A CRIME",R,12,extra='opacity=".8"')
t(o,470,1318,"AGAINST THE SHAREHOLDERS",R,12,extra='opacity=".8"')
t(o,470,1336,"REF 0xG3N0-C0RP-1101",M,12)
o.append('</g>')
t(o,RX-34,92,"STATUS: OPERATIONAL",B,12,"end",extra='opacity=".7"')
o.append(f'<polygon points="{RX-24},82 {RX-4},88 {RX-24},94" fill="{B}"/>')
# --- wordmark + subtitle
big(o,X-6,326,"GENOCORP",140,B,outline=True,ls=10)
big(o,X,382,"SOLUTIONS INC.",26,C,ls=10,w=400)
big(o,X,420,"EMPLOYEE ENGAGEMENT COMMANDMENTS",26,C,ls=6,w=400)
o.append(f'<line x1="{X}" y1="448" x2="{RX}" y2="448" stroke="{R}" stroke-width="3"/>')
# --- the ten articles, wrapped under a hanging indent
arts=[("I.","RESPECT ALL USERS. UNPAID INTERN ABUSE BUILDS CONFIDENCE."),
("II.","PROFANITY WILL BE DEDUCTED FROM YOUR GENOCOIN BALANCE."),
("III.","NSFW REMAINS ILLEGAL PER THE DANZIG ACCORDS OF 2096."),
("IV.","SHARE ONLY CONTENT APPROVED BY STANDARDS AND PRACTICES."),
("V.","NO ADVERTISEMENTS. GENOMARKETPLACE (PATENT PENDING) EXCEPTED."),
("VI.","NAMES AND FACES MUST MATCH THE GENOCORP BRAND IMAGE."),
("VII.","RAIDING WILL BE REPORTED TO OUR CYBER-SECURITY DIVISION."),
("VIII.","GENOLADDER RANK IS EARNED THROUGH OVERTIME, NOT TALENT."),
("IX.","GENOSUPPORT (NEO CHINA) RESPONDS WITHIN 6 TO 8 BUSINESS YEARS."),
("X.","THREATS WILL BE MET BY THE SECURITY DEFENSIVE ASSAULT SQUAD.")]
FS=20; LS=1.5; CW=FS*0.64+LS                      # Plex Mono 0.6em advance + safety (measured 14.3px)
lab=len("ARTICLE VIII. "); body_chars=int((RX-X)/CW)-lab
y=494
for i,(n,s) in enumerate(arts):
  col,w=(R,700) if i==9 else (C,500)
  lines=textwrap.wrap(s,body_chars)
  t(o,X,y,nb(f"ARTICLE {n}".ljust(lab)+lines[0]),col,FS,w=w,ls=LS,extra='xml:space="preserve"')
  for l in lines[1:]:
    y+=26; t(o,X,y,nb(" "*lab+l),col,FS,w=w,ls=LS,extra='xml:space="preserve"')
  y+=40
# --- grievances
gy=y+10
for j,l in enumerate(textwrap.wrap("GRIEVANCES MAY BE FILED WITH HCR (HUMAN-CYBORG RESOURCES). FILING IS NOTED IN YOUR RECORD.",int((RX-X)/(15*0.64+2)))):
  t(o,X,gy+j*22,l,M,15,ls=2)
# --- terminal (from the eye design)
tw,th=560,190; tx,ty=RX-tw,gy+62
assert ty+th<1440, ("terminal overlaps footer", ty+th)
o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="#05061a" fill-opacity=".6" stroke="{B}" stroke-width="1.5"/>')
o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="26" fill="{B}" opacity=".85"/>'); t(o,tx+12,ty+18,"GENOCORP TRUST NETWORK // TTY0","#020205",13,w=700)
o.append(''.join(f'<rect x="{tx+tw-20-i*16}" y="{ty+8}" width="10" height="10" fill="{R if i==0 else "#020205"}"/>' for i in range(3)))
for i,(l,st) in enumerate([("> handshake ........................ ","OK"),("> biometric sync ................... ","OK"),("> loyalty audit ..................... ","PASS"),("> free will module .................. ","DISABLED")]):
  t(o,tx+16,ty+56+i*24,l,M,13); t(o,tx+tw-16,ty+56+i*24,st,R if st=="DISABLED" else B,13,"end",700)
t(o,tx+16,ty+th-16,"citizen@bartholomew:~$",C,13,w=700); o.append(f'<rect x="{tx+219}" y="{ty+th-29}" width="9" height="16" fill="{R}"/>')
# --- footer
t(o,X,1470,"NODE BARTHOLOMEW // SECTOR 09 // UPLINK 0x6E9A2B",M,13,ls=3)
t(o,X,1490,"CLEARANCE: CITIZEN",M,13,ls=3)
o.append(f'<rect x="{X}" y="1504" width="140" height="3" fill="{R}"/>')

name='genotheme-manifesto-portrait'
o.append('</svg>'); open(name+'.svg','w').write("\n".join(o))
cairosvg.svg2png(url=name+'.svg',write_to=name+'-2160x3840.png',output_width=2160,output_height=3840)
cairosvg.svg2png(url=name+'.svg',write_to=name+'-preview.png',output_width=540,output_height=960)
print("article body wraps at",body_chars,"chars; terminal y",ty,"-",ty+th)
