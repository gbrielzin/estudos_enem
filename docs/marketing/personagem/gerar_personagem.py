"""Gera as expressões do personagem do Brazilian.dev (SVG). Uso: python gerar_personagem.py
Mude as cores nas constantes K, SKIN, HAIR, HOOD e BG."""
import os
OUT = os.environ.get("OUT", os.path.dirname(os.path.abspath(__file__)))
K = "#0B0B0B"; SKIN = "#C68B59"; HAIR = "#3B2417"; HOOD = "#F6C400"; BG = "#0F1B2D"

def pupil(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{K}"/>'
            f'<circle cx="{cx+r*0.35:.1f}" cy="{cy-r*0.35:.1f}" r="{max(r*0.3,1.6):.1f}" fill="#fff"/>')

def brow(d): return f'<path d="{d}" fill="none" stroke="{K}" stroke-width="10" stroke-linecap="round"/>'
def mouth_open(d, fill="#5A1010"): return f'<path d="{d}" fill="{fill}" stroke="{K}" stroke-width="7" stroke-linejoin="round"/>'
def line(d): return f'<path d="{d}" fill="none" stroke="{K}" stroke-width="8" stroke-linecap="round"/>'

FACES = {
 "feliz": brow("M186 200 Q212 188 238 200")+brow("M274 200 Q300 188 326 200")+
          pupil(212,254,11)+pupil(300,254,11)+
          mouth_open("M214 308 Q256 362 298 308 Z","#7A1F1F")+
          '<path d="M222 312 Q256 330 290 312 L286 308 L226 308 Z" fill="#fff"/>',
 "surpreso": brow("M184 184 Q212 166 240 184")+brow("M272 184 Q300 166 328 184")+
          pupil(212,254,6)+pupil(300,254,6)+
          mouth_open("M256 304 m-16 0 a16 24 0 1 0 32 0 a16 24 0 1 0 -32 0"),
 "pensando": brow("M186 190 Q212 172 238 190")+brow("M274 208 L326 196")+
          pupil(204,244,10)+pupil(292,244,10)+
          line("M232 328 Q256 318 284 332")+
          f'<text x="392" y="150" font-family="Arial Black,Arial,sans-serif" font-size="84" font-weight="900" fill="#fff" stroke="{K}" stroke-width="3">?</text>',
 "chocado": brow("M184 176 Q212 156 240 176")+brow("M272 176 Q300 156 328 176")+
          pupil(212,254,5)+pupil(300,254,5)+
          mouth_open("M220 304 Q256 392 292 304 Z")+
          '<path d="M236 352 Q256 340 276 352 Q256 372 236 352 Z" fill="#E36A7A"/>',
 "rindo": line("M190 256 Q212 232 234 256")+line("M278 256 Q300 232 322 256")+
          brow("M186 200 Q212 188 238 200")+brow("M274 200 Q300 188 326 200")+
          mouth_open("M208 302 Q256 376 304 302 Z","#7A1F1F")+
          '<path d="M218 308 Q256 332 294 308 L290 302 L222 302 Z" fill="#fff"/>',
 "desconfiado": brow("M184 214 L238 226")+brow("M274 226 L328 214")+
          pupil(220,260,9)+pupil(308,260,9)+
          line("M178 246 L246 258")+line("M266 258 L334 246")+
          line("M232 330 L284 324"),
}

HAIRC = [(170,160,34),(210,128,38),(258,118,40),(306,128,38),(346,160,34),(150,208,26),(362,208,26),(200,170,30),(256,160,34),(312,170,30)]

def svg(face):
    hair_back = "".join(f'<circle cx="{x}" cy="{y}" r="{r+8}" fill="{K}"/>' for x,y,r in HAIRC)
    hair_front = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{HAIR}"/>' for x,y,r in HAIRC)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<defs><clipPath id="c"><circle cx="256" cy="256" r="256"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="512" height="512" fill="{BG}"/>
<path d="M62 520 Q62 398 256 386 Q450 398 450 520 Z" fill="{HOOD}" stroke="{K}" stroke-width="9" stroke-linejoin="round"/>
<path d="M226 388 L226 440 M286 388 L286 440" stroke="#C99F00" stroke-width="9" stroke-linecap="round"/>
<rect x="224" y="338" width="64" height="58" fill="{SKIN}" stroke="{K}" stroke-width="8"/>
<circle cx="146" cy="268" r="22" fill="{SKIN}" stroke="{K}" stroke-width="8"/>
<circle cx="366" cy="268" r="22" fill="{SKIN}" stroke="{K}" stroke-width="8"/>
<ellipse cx="256" cy="256" rx="112" ry="124" fill="{SKIN}" stroke="{K}" stroke-width="9"/>
{hair_back}{hair_front}
<circle cx="212" cy="254" r="40" fill="#fff" fill-opacity=".92" stroke="{K}" stroke-width="8"/>
<circle cx="300" cy="254" r="40" fill="#fff" fill-opacity=".92" stroke="{K}" stroke-width="8"/>
<path d="M252 252 L260 252" stroke="{K}" stroke-width="8"/>
<path d="M172 250 L150 246 M340 250 L362 246" stroke="{K}" stroke-width="8" stroke-linecap="round"/>
{face}
</g></svg>'''

for name, face in FACES.items():
    open(f"{OUT}/{name}.svg","w",encoding="utf-8").write(svg(face))
print("ok")
