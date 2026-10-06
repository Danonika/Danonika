# Cars × README Motion

This header preserves seconds **3–5** of the supplied Cars edit by [@hudsonfilms__](https://www.tiktok.com/@hudsonfilms__/video/7523135205314514183).

README Motion 0.3.0 decodes **all 60 original frames at 958 × 576**, preserves their **30 fps presentation timing**, and embeds them as lossless PNGs inside SVG. It applies no frame sampling, colour palette reduction, resizing, vector tracing, or arbitrary output-size limit. Each embedded PNG was verified byte for byte against an independent FFmpeg extraction.

The text in [header.source.md](header.source.md) remains native SVG text with embedded fonts. The footage is raster imagery inside the SVG container. A gradient behind the text provides contrast; the right edge retains the video's original brightness. Display scaling fits the full frame into the header without changing the stored pixel resolution.

The generated header is **720 × 300 and approximately 37.12 MB**. It loops for two seconds and shows its first frame under reduced motion. It contains no JavaScript or external resources. The complete uploaded MP4 stays local.

## Rebuild

Install README Motion 0.3.0 and FFmpeg, then run:

```sh
python readme-motion/cars-header/generate.py /path/to/Download.mp4 --start 3 --duration 2
# Or provide an explicit FFmpeg executable:
python readme-motion/cars-header/generate.py /path/to/Download.mp4 --ffmpeg /path/to/ffmpeg
```

The start and duration select the excerpt; they do not set a quality level. Longer excerpts retain original resolution and timing. Actual storage, browser, and host limits still apply, and failures must be reported rather than handled by silently reducing quality.

The script writes a content-addressed SVG into `assets/` and records its path, original frame hashes, and timings in [manifest.json](manifest.json). Update the image path in the profile README after rebuilding. The Markdown source remains editable.

[Preview the preserved-quality header](preview.md).
