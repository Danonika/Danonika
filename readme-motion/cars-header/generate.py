"""Build the profile's vector movie header with README Motion 0.2.0.

Usage: python generate.py /path/to/Download.mp4 --ffmpeg /path/to/ffmpeg
Install README Motion with its [trace] extra first. The original video stays local.
"""

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image
from readme_motion.markdown import parse
from readme_motion.render import Background, layout
from readme_motion.svg import SVG, element, export_svg
from readme_motion.trace import trace

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("video", type=Path)
parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
args = parser.parse_args()
if not args.ffmpeg:
    parser.error("Supply --ffmpeg or install FFmpeg on PATH.")
base = Path(__file__).resolve().parent
repo = base.parents[1]
source = base / "header.source.md"
with tempfile.TemporaryDirectory(prefix="readme-motion-header-") as temp:
    work = Path(temp)
    frames = work / "frames"
    frames.mkdir()
    subprocess.run(
        [
            args.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-ss",
            "3",
            "-i",
            str(args.video.resolve()),
            "-t",
            "2",
            "-an",
            "-vf",
            "fps=8,scale=400:-1",
            "-frames:v",
            "16",
            str(frames / "frame-%03d.png"),
        ],
        check=True,
        timeout=60,
    )
    paths = sorted(frames.glob("*.png"))
    if len(paths) != 16:
        raise ValueError("Expected 16 frames from the 3–5 second excerpt.")
    images = []
    for path in paths:
        with Image.open(path) as image:
            images.append(image.convert("RGB"))
    # One shared palette limits path count and keeps colours stable across frames.
    sheet = Image.new("RGB", (images[0].width, images[0].height * len(images)))
    for index, image in enumerate(images):
        sheet.paste(image, (0, index * image.height))
    palette = sheet.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    for path, image in zip(paths, images):
        image.quantize(palette=palette, dither=Image.Dither.NONE).convert("RGB").save(
            path
        )
    stats = trace(frames, work / "traced.svg", max_frames=16, fps=8, width=400)
    blocks, _ = parse(source.read_text())
    pages, _ = layout(blocks, 720, 600, 18, base)
    if len(pages) != 1:
        raise ValueError("Header Markdown must fit on one page.")
    page = pages[0]
    page.height = max(300, page.height)
    export_svg(page, 720, "dark", Background("none"), 2, work / "text.svg")
    front = ET.parse(work / "text.svg").getroot()
    movie = ET.parse(work / "traced.svg").getroot()
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
        "A two-second vector animation from Hudson Films' Cars edit plays behind the text."
    )
    defs = element(root, "defs")
    clip = element(defs, "clipPath", id="header-clip")
    element(clip, "rect", width=720, height=page.height, rx=16)
    gradient = element(defs, "linearGradient", id="header-shade")
    for offset, opacity in [(0, 1), (0.22, 0.97), (0.5, 0.78), (0.8, 0.22), (1, 0.12)]:
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
    destination = repo / "assets" / f"header-cars-{digest}.svg"
    destination.write_bytes(payload)
    manifest = {
        "generator": "README Motion 0.2.0",
        "asset": str(destination.relative_to(repo)),
        "source_sha256": hashlib.sha256(args.video.read_bytes()).hexdigest(),
        "excerpt_start_seconds": 3,
        "duration_seconds": 2,
        "fps": 8,
        "palette_colors": 96,
        "traced": stats,
        "header_width": 720,
        "header_height": page.height,
        "bytes": len(payload),
        "source_url": "https://www.tiktok.com/@hudsonfilms__/video/7523135205314514183",
    }
    (base / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
