# ZenjiJet logo assets

ZenjiJet is the Zenjishoppazz rider (delivery partner) app. Its mark is an
original scooter in the brand navy/orange carrying the Zenjishoppazz bag.

- `zenjijet_mark.py`: draws the mark (SVG rendered with cairosvg) using the
  cleaned bag from `logo_x4.png`. Writes `zenjijet_mark.png` (with speed lines)
  and `zenjijet_icon_mark.png` (without, for small icons).
- `make_logos.py`: builds the in-app logos (`assets/png/app-logo-*.png`), Android
  launcher/adaptive/themed/notification icons, iOS app icon and launch image,
  macOS and web icons. Icons use a peach background so ZenjiJet is easy to tell
  apart from the Zenjishoppazz customer app on the same phone.

```
pip install pillow numpy cairosvg
python3 branding/zenjijet_mark.py && python3 branding/make_logos.py .
```
