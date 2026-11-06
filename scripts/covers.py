"""Render the gallery cover masters into an external build directory."""

import argparse
from io import BytesIO
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

import resvg_py
from PIL import Image

from source_data import ROOT, read


COVER_SIZE = (2010, 1340)
MASTERS = ROOT / "artwork/covers"


def cover_pattern(meta, extension):
    prefix = re.escape(meta["guidPrefix"])
    languages = "|".join(map(re.escape, meta["languages"]))
    return re.compile(
        rf"{prefix}(?:-(?P<language>{languages}))?-cover"
        rf"(?:-(?P<appearance>light|dark))?-(?P<number>[1-9][0-9]*){re.escape(extension)}"
    )


def render_covers(output):
    output = output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("Use a cover output directory outside the checkout")
    pattern = cover_pattern(read("rectoverso.json"), ".svg")
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="cover-render-", dir=output) as temporary:
        rendered = []
        for master in sorted(MASTERS.iterdir()):
            if not master.is_file() or not pattern.fullmatch(master.name):
                raise ValueError(f"Invalid cover master name: {master.name}")
            svg = master.read_text(encoding="utf-8")
            for element in ElementTree.fromstring(svg).iter():
                if element.tag.rsplit("}", 1)[-1] in {"text", "tspan", "textPath"}:
                    raise ValueError(f"Outline text in {master.name}")
                for key, value in element.attrib.items():
                    if key.rsplit("}", 1)[-1] == "href" and not value.startswith(
                        ("#", "data:")
                    ):
                        raise ValueError(f"External resource in {master.name}: {value}")
            target = Path(temporary) / master.with_suffix(".png").name
            png = resvg_py.svg_to_bytes(
                svg_string=svg,
                width=COVER_SIZE[0],
                height=COVER_SIZE[1],
                skip_system_fonts=True,
            )
            with Image.open(BytesIO(png)) as image:
                if image.size != COVER_SIZE:
                    raise ValueError(f"{master.name} must have a 3:2 viewport")
                # Omit an unused alpha channel while preserving transparent artwork.
                if image.mode == "RGBA" and image.getchannel("A").getextrema() == (
                    255,
                    255,
                ):
                    image = image.convert("RGB")
                image.save(target, optimize=True)
            rendered.append(target)
        for target in rendered:
            target.replace(output / target.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    render_covers(parser.parse_args().output)
