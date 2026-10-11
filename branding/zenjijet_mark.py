"""Draw the ZenjiJet mark: an original scooter in brand colours carrying the
Zenjishoppazz bag, with speed lines. Writes branding/zenjijet_mark.png
(transparent, ~2000px wide). Run from the repo root:  python3 branding/zenjijet_mark.py
"""
import io, os
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, NAVY_DARK, ORANGE, TYRE, HUB = '#0A3A6B', '#072A4F', '#D0844A', '#1E2430', '#E8EEF5'

SVG_TEMPLATE = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700">
  <!-- speed lines -->
  <g stroke="{ORANGE}" stroke-linecap="round" fill="none" opacity="SPEED">
    <line x1="20"  y1="430" x2="125" y2="430" stroke-width="16"/>
    <line x1="0"   y1="480" x2="100" y2="480" stroke-width="16" stroke-opacity="0.75"/>
    <line x1="45"  y1="530" x2="130" y2="530" stroke-width="16" stroke-opacity="0.5"/>
  </g>
  <!-- wheels -->
  <g>
    <circle cx="255" cy="575" r="92" fill="{TYRE}"/>
    <circle cx="255" cy="575" r="44" fill="{HUB}"/>
    <circle cx="255" cy="575" r="16" fill="{TYRE}"/>
    <circle cx="770" cy="575" r="92" fill="{TYRE}"/>
    <circle cx="770" cy="575" r="44" fill="{HUB}"/>
    <circle cx="770" cy="575" r="16" fill="{TYRE}"/>
  </g>
  <!-- fork -->
  <line x1="712" y1="250" x2="770" y2="575" stroke="{TYRE}" stroke-width="22" stroke-linecap="round"/>
  <!-- rear carrier holding the bag -->
  <rect x="120" y="356" width="190" height="16" rx="8" fill="{TYRE}"/>
  <rect x="140" y="356" width="14" height="66" rx="7" fill="{TYRE}"/>
  <!-- rear body -->
  <path d="M150,540 C150,440 225,392 335,392 L478,392 L500,482
           C500,522 480,552 440,552 L185,552 C163,552 150,548 150,540 Z" fill="{NAVY}"/>
  <!-- side accent stripe -->
  <path d="M190,500 C215,455 270,438 340,438 L470,438 L478,462 L345,462
           C290,462 245,478 220,508 Z" fill="{ORANGE}"/>
  <!-- seat -->
  <rect x="300" y="360" width="175" height="40" rx="20" fill="{ORANGE}"/>
  <rect x="300" y="360" width="175" height="15" rx="7" fill="#E39A62"/>
  <!-- floorboard -->
  <rect x="430" y="510" width="230" height="42" rx="16" fill="{NAVY_DARK}"/>
  <!-- leg shield / steering column -->
  <path d="M598,552 L652,552 C700,470 728,340 712,238 L676,238
           C668,340 644,445 598,512 Z" fill="{NAVY}"/>
  <!-- front fender -->
  <path d="M690,535 C700,455 840,455 855,535 L822,535 C808,492 735,492 722,535 Z" fill="{NAVY}"/>
  <!-- handlebar, mirror, headlight -->
  <line x1="640" y1="222" x2="760" y2="232" stroke="{TYRE}" stroke-width="20" stroke-linecap="round"/>
  <circle cx="742" cy="272" r="24" fill="#FFE08A" stroke="{NAVY}" stroke-width="8"/>
</svg>'''


def load_bag():
    """Same cleaned, upscaled bag as make_logos.py uses for the app icons."""
    import numpy as np
    from PIL import ImageFilter
    big = Image.open(os.path.join(HERE, 'logo_x4.png')).convert('RGBA')
    b = big.crop((55 * 4 - 8, 8 * 4 - 8, 155 * 4 + 8, 146 * 4 + 8))
    a = np.array(b)
    al = a[:, :, 3].astype(np.float32)
    al[al < 12] = 0
    a[:, :, 3] = np.clip((al - 12) * 255 / 230, 0, 255).astype(np.uint8)
    b = Image.fromarray(a, 'RGBA')
    b = b.crop(b.getbbox())
    rgb = b.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return Image.merge('RGBA', (*rgb.split(), b.split()[3]))


def render(scale=2, speed_lines=True):
    svg = SVG_TEMPLATE.replace('SPEED', '1' if speed_lines else '0')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=1000 * scale, output_height=700 * scale)
    scooter = Image.open(io.BytesIO(png)).convert('RGBA')
    # The brand bag (cleaned master) rides on the carrier as the cargo
    bag = load_bag()
    h = int(250 * scale)
    b = bag.resize((round(bag.width * h / bag.height), h), Image.LANCZOS)
    cx, bottom = int(212 * scale), int(362 * scale)
    canvas = Image.new('RGBA', (scooter.width, scooter.height + 400), (0, 0, 0, 0))
    canvas.alpha_composite(scooter, (0, 400))
    canvas.alpha_composite(b, (cx - b.width // 2, bottom + 400 - b.height))
    return canvas.crop(canvas.getbbox())


if __name__ == '__main__':
    m = render()
    m.save(os.path.join(HERE, 'zenjijet_mark.png'))
    i = render(speed_lines=False)
    i.save(os.path.join(HERE, 'zenjijet_icon_mark.png'))
    print('mark', m.size, 'icon mark', i.size)
