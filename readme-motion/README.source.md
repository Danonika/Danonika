# README Motion

**Markdown in. Motion out.**

Turn an ordinary README into animated image sections for GitHub. Keep writing Markdown; let the renderer handle the motion.

## Words with a pulse

- **Your text stays steady.** A subtle background moves behind it.
- **Two themes, one source.** Light and dark versions build together.
- **A readable way back.** Original Markdown and a text fallback stay available.

## One command

```sh
readme-motion build README.source.md \
  --background grid --theme both \
  --output motion --readme README.md
```

## Made for real Markdown

| Input | Output |
| :--- | :--- |
| Headings, lists and code | Native SVG sections |
| A local GIF or image | A custom background |
| Long documents | Automatic pagination |

> Run it locally. No account, API key, or document upload.

[Read the source](README.source.md) · Built with Python, Pillow, and fonttools.
