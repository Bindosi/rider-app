"""Build every ZenjiJet (rider app) logo / icon asset.

Inputs (this folder):
  zenjijet_mark.png       scooter + Zenjishoppazz bag, with speed lines
  zenjijet_icon_mark.png  same without speed lines (fills small icons better)
Both come from zenjijet_mark.py. Run from the repo root:
  python3 branding/zenjijet_mark.py && python3 branding/make_logos.py .
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)

NAVY = (10, 58, 107)
ORANGE = (208, 132, 74)
PEACH = (255, 205, 160)
GREY = (90, 107, 128)
WHITE = (255, 255, 255)
ICON_BG = (255, 228, 204)   # soft peach: tells ZenjiJet apart from the customer app's white icon
SERIF_BI = '/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

MARK = Image.open(os.path.join(HERE, 'zenjijet_mark.png')).convert('RGBA')
ICON_MARK = Image.open(os.path.join(HERE, 'zenjijet_icon_mark.png')).convert('RGBA')


def out(rel):
    p = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def fit(img, w, h):
    im = img.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    return im


def centered(img, size, box_frac, bg=None, radius=0.0):
    """img fitted into a size x size canvas, occupying box_frac of it."""
    c = Image.new('RGBA', (size, size), (bg + (255,)) if bg else (0, 0, 0, 0))
    m = fit(img, max(1, int(size * box_frac)), max(1, int(size * box_frac)))
    c.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    if radius:
        mask = Image.new('L', (size * 4, size * 4), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1),
                                               radius=int(size * 4 * radius), fill=255)
        c.putalpha(mask.resize((size, size), Image.LANCZOS))
    return c


def silhouette(img, colour=WHITE):
    a = np.array(img).astype(np.int32)
    s = np.zeros_like(a)
    s[:, :, 0], s[:, :, 1], s[:, :, 2] = colour
    s[:, :, 3] = a[:, :, 3]
    return Image.fromarray(s.astype(np.uint8), 'RGBA')


def wordmark(zenji_colour, jet_colour, px=300):
    """'Zenji' + 'Jet' on one baseline."""
    f = ImageFont.truetype(SERIF_BI, px)
    w = int(f.getlength('ZenjiJet')) + px
    h = int(px * 1.6)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, base = px // 4, int(px * 1.15)
    d.text((x, base), 'Zenji', font=f, fill=zenji_colour + (255,), anchor='ls')
    d.text((x + f.getlength('Zenji') + px * 0.02, base), 'Jet', font=f, fill=jet_colour + (255,), anchor='ls')
    return im.crop(im.getbbox())


def text_img(text, font, px, colour):
    f = ImageFont.truetype(font, px)
    l, t, r, b = f.getbbox(text)
    im = Image.new('RGBA', (r - l + 6, b - t + 6), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((3 - l, 3 - t), text, font=f, fill=colour + (255,))
    return im


def lockup(zenji, jet, by_colour, tile=False):
    mark = fit(MARK, 1300, 900)
    if tile:   # navy scooter needs a light tile on dark backgrounds
        t = Image.new('RGBA', (mark.width + 160, mark.height + 160), (0, 0, 0, 0))
        ImageDraw.Draw(t).rounded_rectangle((0, 0, t.width - 1, t.height - 1), radius=150, fill=WHITE + (255,))
        t.alpha_composite(mark, (80, 80))
        mark = t
    word = wordmark(zenji, jet)
    by = text_img('by Zenjishoppazz', SANS, 92, by_colour)
    W = max(mark.width, word.width, by.width) + 40
    H = mark.height + 60 + word.height + 30 + by.height
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    y = 0
    for im, gap in ((mark, 60), (word, 30), (by, 0)):
        c.alpha_composite(im, ((W - im.width) // 2, y))
        y += im.height + gap
    return c.crop(c.getbbox())


# ---------------------------------------------------------------- in-app logos
# app-logo-dark = dark text, used on the white splash / login / register screens
lockup(NAVY, ORANGE, GREY).save(out('assets/png/app-logo-dark.png'), optimize=True)
# app-logo-light = light text, for dark backgrounds
lockup(WHITE, PEACH, (200, 210, 225), tile=True).save(out('assets/png/app-logo-light.png'), optimize=True)

# ---------------------------------------------------------------- Android
dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
res = 'android/app/src/main/res'
for d, k in dens.items():
    centered(ICON_MARK, round(48 * k), 0.82, bg=ICON_BG, radius=0.22).save(out(f'{res}/mipmap-{d}/ic_launcher.png'))
    fs = round(108 * k)   # adaptive icon: keep the mark inside the 66dp safe zone
    centered(ICON_MARK, fs, 0.52).save(out(f'{res}/mipmap-{d}/ic_launcher_foreground.png'))
    centered(silhouette(ICON_MARK), fs, 0.52).save(out(f'{res}/mipmap-{d}/ic_launcher_monochrome.png'))
    fit(MARK, round(200 * k), round(140 * k)).save(out(f'{res}/mipmap-{d}/launch_image.png'))

with open(out(f'{res}/mipmap-anydpi-v26/ic_launcher.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n'
            '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <background android:drawable="@color/ic_launcher_background" />\n'
            '    <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n'
            '    <monochrome android:drawable="@mipmap/ic_launcher_monochrome" />\n'
            '</adaptive-icon>\n')
with open(out(f'{res}/values/ic_launcher_background.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
            '    <color name="ic_launcher_background">#%02X%02X%02X</color>\n</resources>\n' % ICON_BG)

# status-bar notification icon: single-colour scooter silhouette
for d in ('drawable', 'drawable-v21'):
    centered(silhouette(ICON_MARK), 192, 0.92).save(out(f'{res}/{d}/notification.png'))

# ---------------------------------------------------------------- iOS
iconset = 'ios/Runner/Assets.xcassets/AppIcon.appiconset'
contents = json.load(open(out(f'{iconset}/Contents.json')))
needed = set()
for im in contents['images']:
    fn = im.get('filename')
    if fn:
        pt = float(im['size'].split('x')[0]); sc = float(im['scale'].rstrip('x'))
        needed.add((fn, round(pt * sc)))
for fn, px in sorted(needed):
    centered(ICON_MARK, px, 0.80, bg=ICON_BG).convert('RGB').save(out(f'{iconset}/{fn}'))
for fn in os.listdir(out(iconset)):
    if fn.endswith('.png') and fn not in {n for n, _ in needed}:
        os.remove(out(f'{iconset}/{fn}'))
launch = 'ios/Runner/Assets.xcassets/LaunchImage.imageset'
for sc, fn in ((1, 'LaunchImage.png'), (2, 'LaunchImage@2x.png'), (3, 'LaunchImage@3x.png')):
    fit(MARK, 200 * sc, 140 * sc).save(out(f'{launch}/{fn}'))
json.dump({'images': [{'idiom': 'universal', 'filename': f, 'scale': s} for s, f in
                      (('1x', 'LaunchImage.png'), ('2x', 'LaunchImage@2x.png'), ('3x', 'LaunchImage@3x.png'))],
           'info': {'version': 1, 'author': 'xcode'}}, open(out(f'{launch}/Contents.json'), 'w'), indent=2)

# ---------------------------------------------------------------- macOS
mac = 'macos/Runner/Assets.xcassets/AppIcon.appiconset'
if os.path.isdir(out(mac)):
    for s in (16, 32, 64, 128, 256, 512, 1024):
        c = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        inner = centered(ICON_MARK, round(s * 0.80), 0.80, bg=ICON_BG, radius=0.225)
        c.alpha_composite(inner, ((s - inner.width) // 2, (s - inner.height) // 2))
        c.save(out(f'{mac}/app_icon_{s}.png'))

# ---------------------------------------------------------------- web
centered(ICON_MARK, 32, 0.92, bg=ICON_BG).convert('RGB').save(out('web/favicon.png'))
centered(ICON_MARK, 192, 0.80, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-192.png'))
centered(ICON_MARK, 512, 0.80, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-512.png'))
centered(ICON_MARK, 192, 0.64, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-maskable-192.png'))
centered(ICON_MARK, 512, 0.64, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-maskable-512.png'))
print('done')
