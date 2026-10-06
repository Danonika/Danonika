"""Build the profile's original-quality movie header with README Motion 0.3.0.

Usage: python generate.py /path/to/Download.mp4 --ffmpeg /path/to/ffmpeg
Install README Motion first. The original video stays local; decoded frames are embedded losslessly.
"""

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from readme_motion.animate import animate
from readme_motion.markdown import parse
from readme_motion.render import Background, layout
from readme_motion.svg import SVG, element, export_svg

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("video", type=Path)
parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
parser.add_argument("--start", type=float, default=3)
parser.add_argument("--duration", type=float, default=2)
args = parser.parse_args()
if not args.ffmpeg:
    parser.error("Supply --ffmpeg or install FFmpeg on PATH.")
base = Path(__file__).resolve().parent
repo = base.parents[1]
source = base / "header.source.md"
with tempfile.TemporaryDirectory(prefix="readme-motion-header-") as temp:
    work = Path(temp)
    stats = animate(
        args.video,
        work / "original.svg",
        start=args.start,
        seconds=args.duration,
        ffmpeg=args.ffmpeg,
    )
    blocks, _ = parse(source.read_text())
    pages, _ = layout(blocks, 720, 600, 18, base)
    if len(pages) != 1:
        raise ValueError("Header Markdown must fit on one page.")
    page = pages[0]
    page.height = max(300, page.height)
    export_svg(page, 720, "dark", Background("none"), 2, work / "text.svg")
    front = ET.parse(work / "text.svg").getroot()
    movie = ET.parse(work / "original.svg").getroot()
    root = ET.Element(
        f"{{{SVG}}}svg",
        {
            "viewBox": f"0 0 720 {page.height}",
            "width": "720",
            "height": str(page.height),
            "role": "img",
            "aria-labelledby": "header-title header-desc",
        },
    )
    element(
        root, "title", id="header-title"
    ).text = "Daniyar Kuttymbek — Software Engineer"
    element(root, "desc", id="header-desc").text = (
        "Go, distributed systems, and security automation. Secure systems. Intelligent tools. "
        "Original-resolution video frames from Hudson Films' Cars edit play behind the text."
    )
    defs = element(root, "defs")
    clip = element(defs, "clipPath", id="header-clip")
    element(clip, "rect", width=720, height=page.height, rx=16)
    gradient = element(defs, "linearGradient", id="header-shade")
    for offset, opacity in [(0, 1), (0.22, 0.97), (0.5, 0.78), (0.8, 0.08), (1, 0)]:
        element(
            gradient, "stop", offset=offset, stop_color="#080e19", stop_opacity=opacity
        )
    for definition in front.findall(f"{{{SVG}}}defs"):
        for child in definition:
            defs.append(copy.deepcopy(child))
    group = element(root, "g", clip_path="url(#header-clip)")
    element(group, "rect", width=720, height=page.height, fill="#080e19")
    # Fit the complete video frame on the right; preserve its watermark and proportions.
    movie.attrib.update(
        {
            "x": "190",
            "y": "0",
            "width": "530",
            "height": str(page.height),
            "preserveAspectRatio": "xMidYMid meet",
        }
    )
    movie.attrib.pop("aria-labelledby", None)
    for title in movie.findall(f"{{{SVG}}}title"):
        movie.remove(title)
    group.append(movie)
    element(group, "rect", width=720, height=page.height, fill="url(#header-shade)")
    for child in front:
        if child.tag in {f"{{{SVG}}}text", f"{{{SVG}}}line"}:
            group.append(copy.deepcopy(child))
    element(
        root,
        "rect",
        x=0.5,
        y=0.5,
        width=719,
        height=page.height - 1,
        rx=16,
        fill="none",
        stroke="#29425a",
    )
    payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    digest = hashlib.sha256(payload).hexdigest()[:12]
    destination = repo / "assets" / f"header-cars-original-{digest}.svg"
    destination.write_bytes(payload)
    manifest = {
        "generator": "README Motion 0.3.0",
        "asset": str(destination.relative_to(repo)),
        "source_sha256": hashlib.sha256(args.video.read_bytes()).hexdigest(),
        "excerpt_start_seconds": args.start,
        "duration_seconds": stats["duration_ms"] / 1000,
        "average_fps": stats["frames"] * 1000 / stats["duration_ms"],
        "quality": "original decoded pixels and presentation timing",
        "media": stats,
        "header_width": 720,
        "header_height": page.height,
        "bytes": len(payload),
        "source_url": "https://www.tiktok.com/@hudsonfilms__/video/7523135205314514183",
    }
    (base / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
