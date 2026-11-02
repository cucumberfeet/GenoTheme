import random, cairosvg
exec(open('more.py').read().split('# 3: Skyline')[0])
def big(o,x,y,s,size,col,fam="Oswald",w=700,ls=4,outline=False,anchor="start",op=1):
  if outline: o.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-weight="{w}" font-size="{size}" fill="none" stroke="{col}" stroke-width="2" letter-spacing="{ls}" text-anchor="{anchor}" opacity="{op}">{s}</text>')
  else: o.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-weight="{w}" font-size="{size}" fill="{col}" letter-spacing="{ls}" text-anchor="{anchor}" opacity="{op}">{s}</text>')

# A: Manifesto
o=base(21,.3,.4)
big(o,360,330,"GENOCORP",220,B,outline=True,ls=18)
big(o,366,400,"SOLUTIONS INC. — EMPLOYEE ENGAGEMENT COMMANDMENTS",30,C,ls=10,w=400)
o.append(f'<line x1="366" y1="430" x2="1700" y2="430" stroke="{R}" stroke-width="3"/>')
arts=["ARTICLE I.    RESPECT ALL USERS. UNPAID INTERN ABUSE BUILDS CONFIDENCE.",
"ARTICLE II.   PROFANITY WILL BE DEDUCTED FROM YOUR GENOCOIN BALANCE.",
"ARTICLE III.  NSFW REMAINS ILLEGAL PER THE DANZIG ACCORDS OF 2096.",
"ARTICLE IV.   SHARE ONLY CONTENT APPROVED BY STANDARDS AND PRACTICES.",
"ARTICLE V.    NO ADVERTISEMENTS. GENOMARKETPLACE (PATENT PENDING) EXCEPTED.",
"ARTICLE VI.   NAMES AND FACES MUST MATCH THE GENOCORP BRAND IMAGE.",
"ARTICLE VII.  RAIDING WILL BE REPORTED TO OUR CYBER-SECURITY DIVISION.",
"ARTICLE VIII. GENOLADDER RANK IS EARNED THROUGH OVERTIME, NOT TALENT.",
"ARTICLE IX.   GENOSUPPORT (NEO CHINA) RESPONDS WITHIN 6 TO 8 BUSINESS YEARS.",
"ARTICLE X.    THREATS WILL BE MET BY THE SECURITY DEFENSIVE ASSAULT SQUAD."]
for i,s in enumerate(arts):
  t(o,366,510+i*44,s.replace("  ","&#160;&#160;"),C if i!=9 else R,22,w=500 if i!=9 else 700,ls=2,extra='xml:space="preserve"')
t(o,366,982,"GRIEVANCES MAY BE FILED WITH HCR (HUMAN-CYBORG RESOURCES). FILING IS NOTED IN YOUR RECORD.",M,15,ls=2)
t(o,366,1300,"NODE BARTHOLOMEW // SECTOR 09 // UPLINK 0x6E9A2B // CLEARANCE: CITIZEN",M,13,ls=3)
o.append(f'<rect x="366" y="1314" width="140" height="3" fill="{R}"/>')
save(o,'genotheme-manifesto')

# B: System log
o=base(22,.4,.3)
msgs=["auth.trust: citizen session verified","biomon: heart rate within loyal parameters","netd: uplink to GENOCORP CORE established",
"ledger: 0.02 credits deducted (breathing fee)","sentiment: mood scan complete — CONTENT","vault: zero-knowledge sync OK",
"hr.bot: reminder — smiling is mandatory","adsvc: injecting dream sponsorship slot 3/5","cam.07: subject present at desk",
"policy: terms of service updated (v4,221)","kernel: free will module not found — continuing","audit: loyalty index 99.7%",
"pwr: grid allocation approved by Board","geo: location shared with 14 partners","sched: next performance review in 03:14:07"]
y=120; i=0
lines=[]
while y<1340:
  m=random.choice(msgs); ts=f"[{random.randint(0,99999):05d}.{random.randint(0,999999):06d}]"
  col=M; op=.55
  if "free will" in m or "breathing" in m: col=R; op=.95
  elif random.random()<.12: col=C; op=.9
  maxx=2200 if y<900 else 1500
  lines.append((y,ts,m,col,op)); y+=30
for (y,ts,m,col,op) in lines:
  t(o,360,y,f"{ts} {m}",col,17,ls=1,extra=f'opacity="{op}"')
big(o,2480,250,"ALL SYSTEMS",120,C,anchor="end",ls=8,w=300)
big(o,2480,380,"NOMINAL",120,B,anchor="end",ls=8,outline=True)
t(o,2480,430,"GENOCORP TRUST NETWORK // NOTHING TO SEE HERE",R,16,"end",700,4)
save(o,'genotheme-syslog')

# C: Poster
o=base(23,.35,.5)
words=[("COMPLIANCE",False,C),("IS",True,B),("FREEDOM.",False,R)]
for i,(w,ol,col) in enumerate(words):
  big(o,350,420+i*250,w,280,col,outline=ol,ls=6,w=700 if not ol else 400)
t(o,360,1210,"A MESSAGE FROM THE GENOCORP BOARD OF DIRECTORS. THIS MESSAGE CANNOT BE DISMISSED.",M,16,ls=3)
t(o,360,1236,"FINE PRINT: GENOCORP IS NOT RESPONSIBLE FOR LOSS OF IDENTITY, MEMORY, OR WILL TO RESIST.",M,13,ls=2)
t(o,2480,100,"GENOCORP // PUBLIC NOTICE 0x1101",C,15,"end",700,4)
o.append(f'<rect x="2340" y="114" width="140" height="3" fill="{R}"/>')
save(o,'genotheme-poster')
