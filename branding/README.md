# ZenjiJet logo assets

ZenjiJet is the Zenjishoppazz rider (delivery partner) app.

- `zenjijet_design_sheet.png`: the approved design sheet (logo, dark version,
  app icons, compact logo, monochrome / favicon).
- `zj_*.png`: master artwork cut from the sheet, AI-upscaled 4x with a clean
  transparent background:
  - `zj_mark_full.png` rider + scooter + box with speed lines
  - `zj_mark_icon.png` same without speed lines (small icons)
  - `zj_word.png`, `zj_word_white.png` the ZenjiJet wordmark (light / dark backgrounds)
  - `zj_tag.png`, `zj_tag_light.png` "by Zenjishoppazz"
  - `zj_z_white.png` the Z monogram (notification icon, favicon)
- `make_logos.py`: builds every logo and icon in the app from the masters
  (in-app logos, Android launcher / adaptive / themed / notification icons,
  iOS app icon and launch image, macOS and web icons). App icons use the warm
  peach background.

```
pip install pillow numpy
python3 branding/make_logos.py .
```

The `extract_*.py` scripts document how the masters were cut from the sheet
(OpenCV EDSR x4 super-resolution, then background removal). You only need them
if the design sheet changes; a high-resolution or SVG original from the
designer would replace this step.
