"""Build every ZenjiJet (rider app) logo / icon asset from the master artwork.

Masters (this folder), cut from zenjijet_design_sheet.png and AI-upscaled 4x
(see extract_parts.py):
  zj_mark_full.png    rider + scooter + delivery box, with speed lines
  zj_mark_icon.png    same without speed lines (reads better on small icons)
  zj_word.png         'ZenjiJet' wordmark (navy + orange)
  zj_word_white.png   same with white 'Zenji' for dark backgrounds
  zj_tag.png / zj_tag_light.png   'by Zenjishoppazz'
  zj_z_white.png      the white 'Z' monogram

Run from the repo root:  python3 branding/make_logos.py .
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)

ICON_BG = (255, 228, 204)   # warm peach background for app icons
NAVY = (12, 30, 60)         # badge colour for the small Z (favicon)


def load(name):
    return Image.open(os.path.join(HERE, name)).convert('RGBA')


MARK = load('zj_mark_full.png')
ICON_MARK = load('zj_mark_icon.png')
WORD, WORD_WHITE = load('zj_word.png'), load('zj_word_white.png')
TAG, TAG_LIGHT = load('zj_tag.png'), load('zj_tag_light.png')


def clean_z():
    """Smooth, crisp white Z: upscale the extracted monogram, threshold, soften edges."""
    z = load('zj_z_white.png')
    a = z.split()[3].resize((z.width * 6, z.height * 6), Image.LANCZOS)
    a = a.point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.GaussianBlur(2.2))
    out = Image.new('RGBA', a.size, (255, 255, 255, 0))
    out.putalpha(a)
    return out.crop(out.getbbox())


Z = clean_z()


def out(rel):
    p = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def fit(img, w, h):
    im = img.copy()
    im.thumbnail((max(1, w), max(1, h)), Image.LANCZOS)
    return im


def centered(img, size, box_frac, bg=None, radius=0.0):
    c = Image.new('RGBA', (size, size), (bg + (255,)) if bg else (0, 0, 0, 0))
    m = fit(img, int(size * box_frac), int(size * box_frac))
    c.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    if radius:
        mask = Image.new('L', (size * 4, size * 4), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1),
                                               radius=int(size * 4 * radius), fill=255)
        c.putalpha(mask.resize((size, size), Image.LANCZOS))
    return c


def silhouette(img, cut_light=True):
    """White single-colour version; light details (Z on box, wheel hubs) become holes."""
    a = np.array(img).astype(np.int32)
    al = a[:, :, 3].copy()
    if cut_light:
        light = a[:, :, :3].mean(2) > 200
        al[light] = 0
    s = np.zeros_like(a); s[:, :, :3] = 255; s[:, :, 3] = al
    return Image.fromarray(s.astype(np.uint8), 'RGBA')


def lockup(word, tag):
    """Mark on top, wordmark below, tagline right-aligned under the wordmark (as designed)."""
    mark = MARK
    w = fit(word, int(mark.width * 1.02), 10_000)
    t = fit(tag, int(w.width * 0.50), 10_000)
    W = max(mark.width, w.width) + 20
    H = mark.height + 40 + w.height + 18 + t.height
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c.alpha_composite(mark, ((W - mark.width) // 2, 0))
    wx = (W - w.width) // 2
    c.alpha_composite(w, (wx, mark.height + 40))
    c.alpha_composite(t, (wx + w.width - t.width - int(w.width * 0.02), mark.height + 40 + w.height + 18))
    return c.crop(c.getbbox())


# ---------------------------------------------------------------- in-app logos
fit(lockup(WORD, TAG), 900, 900).save(out('assets/png/app-logo-dark.png'), optimize=True)        # light screens
fit(lockup(WORD_WHITE, TAG_LIGHT), 900, 900).save(out('assets/png/app-logo-light.png'), optimize=True)  # dark screens

# ---------------------------------------------------------------- Android
dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
res = 'android/app/src/main/res'
for d, k in dens.items():
    centered(ICON_MARK, round(48 * k), 0.86, bg=ICON_BG, radius=0.22).save(out(f'{res}/mipmap-{d}/ic_launcher.png'))
    fs = round(108 * k)                       # adaptive icon: stay inside the 66dp safe zone
    centered(ICON_MARK, fs, 0.60).save(out(f'{res}/mipmap-{d}/ic_launcher_foreground.png'))
    centered(silhouette(ICON_MARK), fs, 0.60).save(out(f'{res}/mipmap-{d}/ic_launcher_monochrome.png'))
    fit(MARK, round(220 * k), round(130 * k)).save(out(f'{res}/mipmap-{d}/launch_image.png'))

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

# status-bar notification icon: the white Z monogram (clear at 24dp)
for d in ('drawable', 'drawable-v21'):
    centered(Z, 192, 0.86).save(out(f'{res}/{d}/notification.png'))

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
    centered(ICON_MARK, px, 0.84, bg=ICON_BG).convert('RGB').save(out(f'{iconset}/{fn}'))
for fn in os.listdir(out(iconset)):
    if fn.endswith('.png') and fn not in {n for n, _ in needed}:
        os.remove(out(f'{iconset}/{fn}'))
launch = 'ios/Runner/Assets.xcassets/LaunchImage.imageset'
for sc, fn in ((1, 'LaunchImage.png'), (2, 'LaunchImage@2x.png'), (3, 'LaunchImage@3x.png')):
    fit(MARK, 220 * sc, 130 * sc).save(out(f'{launch}/{fn}'))
json.dump({'images': [{'idiom': 'universal', 'filename': f, 'scale': s} for s, f in
                      (('1x', 'LaunchImage.png'), ('2x', 'LaunchImage@2x.png'), ('3x', 'LaunchImage@3x.png'))],
           'info': {'version': 1, 'author': 'xcode'}}, open(out(f'{launch}/Contents.json'), 'w'), indent=2)

# ---------------------------------------------------------------- macOS
mac = 'macos/Runner/Assets.xcassets/AppIcon.appiconset'
if os.path.isdir(out(mac)):
    for s in (16, 32, 64, 128, 256, 512, 1024):
        c = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        inner = centered(ICON_MARK, round(s * 0.80), 0.84, bg=ICON_BG, radius=0.225)
        c.alpha_composite(inner, ((s - inner.width) // 2, (s - inner.height) // 2))
        c.save(out(f'{mac}/app_icon_{s}.png'))

# ---------------------------------------------------------------- web
centered(Z, 32, 0.72, bg=NAVY, radius=0.22).save(out('web/favicon.png'))   # tiny: the Z badge, as designed
centered(ICON_MARK, 192, 0.84, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-192.png'))
centered(ICON_MARK, 512, 0.84, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-512.png'))
centered(ICON_MARK, 192, 0.64, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-maskable-192.png'))
centered(ICON_MARK, 512, 0.64, bg=ICON_BG).convert('RGB').save(out('web/icons/Icon-maskable-512.png'))
print('done')
