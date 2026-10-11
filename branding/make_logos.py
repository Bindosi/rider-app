"""Build every Zenjishoppazz Rider logo / icon asset from the AI-upscaled source.

Inputs (scratchpad): logo_x4.png  (EDSR 4x upscale of the transparent logo)
Writes into the repo given as argv[1].
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1]

NAVY = (10, 58, 107)        # wordmark colour sampled from the original
ORANGE = (208, 132, 74)     # tagline colour sampled from the original
PEACH = (255, 205, 160)     # tagline on blue backgrounds (orange is too dark there)
WHITE = (255, 255, 255)
FONT_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
FONT_BOLD_ITALIC = '/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'


def out(rel):
    p = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# ---------------------------------------------------------------- the bag
big = Image.open(os.path.join(HERE, 'logo_x4.png')).convert('RGBA')
bag = big.crop((55 * 4 - 8, 8 * 4 - 8, 155 * 4 + 8, 146 * 4 + 8))
a = np.array(bag)
alpha = a[:, :, 3].astype(np.float32)
alpha[alpha < 12] = 0                       # drop upscaling haze around the edges
alpha = np.clip((alpha - 12) * 255 / 230, 0, 255)
a[:, :, 3] = alpha.astype(np.uint8)
bag = Image.fromarray(a, 'RGBA')
bag = bag.crop(bag.getbbox())
# gentle sharpening of colour only (keeps alpha edges smooth)
rgb = bag.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
bag = Image.merge('RGBA', (*rgb.split(), bag.split()[3]))
print('bag master', bag.size)


def bag_h(h):
    w = round(bag.width * h / bag.height)
    return bag.resize((w, h), Image.LANCZOS)


def silhouette(img, colour=WHITE, cut_logo=True):
    """Single-colour silhouette; the white Z on the bag becomes see-through."""
    arr = np.array(img).astype(np.int32)
    al = arr[:, :, 3].copy()
    if cut_logo:
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        light = (r + g + b) / 3
        z = ((light > 170) & (b > 150)).astype(np.uint8)   # the light Z stroke
        import cv2
        k = max(3, int(round(img.height * 0.022)))         # bolden so it reads at 24px
        z = cv2.morphologyEx(z, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        z = cv2.dilate(z, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        body = (al > 128).astype(np.uint8)
        body = cv2.erode(body, np.ones((3, 3), np.uint8))  # keep a solid outline around the Z
        al[(z > 0) & (body > 0)] = 0
    s = np.zeros_like(arr)
    s[:, :, 0], s[:, :, 1], s[:, :, 2] = colour
    s[:, :, 3] = al
    return Image.fromarray(s.astype(np.uint8), 'RGBA')


def square_icon(size, bg=WHITE, fill=0.74, radius=0.0, transparent_outside=False):
    canvas = Image.new('RGBA', (size, size), bg + (255,))
    if radius:
        mask = Image.new('L', (size * 4, size * 4), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1),
                                               radius=int(size * 4 * radius), fill=255)
        mask = mask.resize((size, size), Image.LANCZOS)
        canvas.putalpha(mask)
    b = bag_h(max(1, round(size * fill)))
    canvas.alpha_composite(b, ((size - b.width) // 2, (size - b.height) // 2))
    if not transparent_outside and not radius:
        canvas = canvas.convert('RGB')
    return canvas


def text_img(text, font_path, px, colour):
    f = ImageFont.truetype(font_path, px)
    l, t, r, b = f.getbbox(text)
    im = Image.new('RGBA', (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), text, font=f, fill=colour + (255,))
    return im


def lockup(name_colour, tag_colour, tile=False, tag_text='Duka kiganjani mwako', tag_font=None, tag_px=104):
    """Bag above 'Zenjishoppazz' above tagline, like the original artwork."""
    mark_h = 520
    if tile:
        side = 640
        t = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        ImageDraw.Draw(t).rounded_rectangle((0, 0, side - 1, side - 1), radius=150,
                                            fill=WHITE + (255,))
        b = bag_h(mark_h)
        t.alpha_composite(b, ((side - b.width) // 2, (side - b.height) // 2))
        mark = t
    else:
        mark = bag_h(mark_h + 60)
    name = text_img('Zenjishoppazz', FONT_BOLD, 190, name_colour)
    tag = text_img(tag_text, tag_font or FONT_BOLD_ITALIC, tag_px, tag_colour)
    W = max(mark.width, name.width, tag.width) + 40
    gap1, gap2 = 60, 22
    H = mark.height + gap1 + name.height + gap2 + tag.height + 20
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    y = 0
    for im, gap in ((mark, gap1), (name, gap2), (tag, 0)):
        c.alpha_composite(im, ((W - im.width) // 2, y))
        y += im.height + gap
    return c.crop(c.getbbox())



RIDER_BG = (255, 228, 204)  # soft peach from the logo's orange: tells the rider icon apart from the customer app
SANS_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def spaced(text):
    return '\u2009'.join(text)   # thin spaces for letter-spacing


# ---------------------------------------------------------------- in-app logos
# app-logo-dark = dark text, used on the white splash / login / register screens
lockup(NAVY, ORANGE, tag_text=spaced('RIDER'), tag_font=SANS_BOLD, tag_px=120).save(
    out('assets/png/app-logo-dark.png'), optimize=True)
# app-logo-light = white text on a tile, for dark backgrounds
lockup(WHITE, PEACH, tile=True, tag_text=spaced('RIDER'), tag_font=SANS_BOLD, tag_px=120).save(
    out('assets/png/app-logo-light.png'), optimize=True)

# ---------------------------------------------------------------- Android
dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
res = 'android/app/src/main/res'
for d, k in dens.items():
    s = round(48 * k)
    square_icon(s, bg=RIDER_BG, fill=0.70, radius=0.22).save(out(f'{res}/mipmap-{d}/ic_launcher.png'))
    fs = round(108 * k)
    fg = Image.new('RGBA', (fs, fs), (0, 0, 0, 0))
    b = bag_h(round(fs * 0.50))
    fg.alpha_composite(b, ((fs - b.width) // 2, (fs - b.height) // 2))
    fg.save(out(f'{res}/mipmap-{d}/ic_launcher_foreground.png'))
    mono = Image.new('RGBA', (fs, fs), (0, 0, 0, 0))
    sb = silhouette(b)
    mono.alpha_composite(sb, ((fs - sb.width) // 2, (fs - sb.height) // 2))
    mono.save(out(f'{res}/mipmap-{d}/ic_launcher_monochrome.png'))
    bag_h(round(120 * k)).save(out(f'{res}/mipmap-{d}/launch_image.png'))

with open(out(f'{res}/mipmap-anydpi-v26/ic_launcher.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n'
            '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <background android:drawable="@color/ic_launcher_background" />\n'
            '    <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n'
            '    <monochrome android:drawable="@mipmap/ic_launcher_monochrome" />\n'
            '</adaptive-icon>\n')
with open(out(f'{res}/values/ic_launcher_background.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
            '    <color name="ic_launcher_background">#%02X%02X%02X</color>\n</resources>\n' % RIDER_BG)

for d in ('drawable', 'drawable-v21'):
    n = Image.new('RGBA', (192, 192), (0, 0, 0, 0))
    sb = silhouette(bag_h(168))
    n.alpha_composite(sb, ((192 - sb.width) // 2, (192 - sb.height) // 2))
    n.save(out(f'{res}/{d}/notification.png'))

# ---------------------------------------------------------------- iOS
iconset = 'ios/Runner/Assets.xcassets/AppIcon.appiconset'
contents = json.load(open(out(f'{iconset}/Contents.json')))
needed = set()
for im in contents['images']:
    fn = im.get('filename')
    if not fn:
        continue
    pt = float(im['size'].split('x')[0]); sc = float(im['scale'].rstrip('x'))
    needed.add((fn, round(pt * sc)))
for fn, px in sorted(needed):
    square_icon(px, bg=RIDER_BG, fill=0.74).save(out(f'{iconset}/{fn}'))
for fn in os.listdir(out(iconset)):
    if fn.endswith('.png') and fn not in {n for n, _ in needed}:
        os.remove(out(f'{iconset}/{fn}')); print('removed unused', fn)
launch = 'ios/Runner/Assets.xcassets/LaunchImage.imageset'
for sc, fn in ((1, 'LaunchImage.png'), (2, 'LaunchImage@2x.png'), (3, 'LaunchImage@3x.png')):
    bag_h(120 * sc).save(out(f'{launch}/{fn}'))
json.dump({'images': [{'idiom': 'universal', 'filename': f, 'scale': s} for s, f in
                      (('1x', 'LaunchImage.png'), ('2x', 'LaunchImage@2x.png'), ('3x', 'LaunchImage@3x.png'))],
           'info': {'version': 1, 'author': 'xcode'}}, open(out(f'{launch}/Contents.json'), 'w'), indent=2)

# ---------------------------------------------------------------- macOS
mac = 'macos/Runner/Assets.xcassets/AppIcon.appiconset'
if os.path.isdir(out(mac)):
    for s in (16, 32, 64, 128, 256, 512, 1024):
        c = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        inner = square_icon(round(s * 0.80), bg=RIDER_BG, fill=0.74, radius=0.225)
        c.alpha_composite(inner, ((s - inner.width) // 2, (s - inner.height) // 2))
        c.save(out(f'{mac}/app_icon_{s}.png'))

# ---------------------------------------------------------------- web
square_icon(32, bg=RIDER_BG, fill=0.86).save(out('web/favicon.png'))
square_icon(192, bg=RIDER_BG, fill=0.74).save(out('web/icons/Icon-192.png'))
square_icon(512, bg=RIDER_BG, fill=0.74).save(out('web/icons/Icon-512.png'))
square_icon(192, bg=RIDER_BG, fill=0.60).save(out('web/icons/Icon-maskable-192.png'))
square_icon(512, bg=RIDER_BG, fill=0.60).save(out('web/icons/Icon-maskable-512.png'))
print('done')
