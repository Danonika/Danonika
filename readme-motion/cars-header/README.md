# Cars × README Motion

The profile header uses seconds **3–5** of the supplied Cars edit by [@hudsonfilms__](https://www.tiktok.com/@hudsonfilms__/video/7523135205314514183).

README Motion 0.2.0 traces 16 sampled frames into SVG paths at 8 fps. One shared 96-colour palette keeps the colours stable and reduces path count. The Markdown in [header.source.md](header.source.md) is rendered as native SVG text with embedded subset fonts, then layered over the animation and a dark gradient for readability.

The result is a **720 × 300 animated SVG, approximately 4.32 MB**, containing vector paths and text. It loops for two seconds and shows its first frame for reduced-motion preferences. It uses no scripts, embedded video, or remote fonts. Tracing gives the footage a stylized look. The complete uploaded MP4 stays local.

## Rebuild

Install README Motion 0.2.0 with its `trace` extra, plus FFmpeg, then run:

```sh
python readme-motion/cars-header/generate.py /path/to/Download.mp4
# Or provide an explicit FFmpeg executable:
python readme-motion/cars-header/generate.py /path/to/Download.mp4 --ffmpeg /path/to/ffmpeg
```

The script writes a content-addressed SVG into `assets/` and records its path and settings in [manifest.json](manifest.json). Update the image path at the top of the profile README after rebuilding. Source text is in a separate Markdown file and remains editable.

Verified locally in light and dark layouts at 720 px and 390 px display widths. The existing profile text, links, toolbox, private-stats workflow, and calendar artwork remain unchanged.
