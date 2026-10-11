# Zenjishoppazz Rider logo assets

- `original-logo.png`: the logo as supplied.
- `logo_x4.png`: AI-upscaled 4x source used for everything.
- `make_logos.py`: regenerates the in-app logos (`assets/png/app-logo-*.png`),
  Android launcher/adaptive/themed/notification icons, iOS app icon and launch
  image, macOS and web icons. The rider icon uses a peach background so it is
  easy to tell apart from the customer app on the same phone.

```
pip install pillow numpy opencv-python-headless
python3 branding/make_logos.py .
```
