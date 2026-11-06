"""Check rendered gallery cover names, language coverage and the language-pill corner."""

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sys

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from covers import COVER_SIZE, cover_pattern
from source_data import read


CORNER = (1608, 0, 2010, 336)  # Includes row y = 335.
CORNER_TOLERANCE = 4


def verify(output):
    meta = read("rectoverso.json")
    languages = set(meta["languages"])
    pattern = cover_pattern(meta, ".png")
    coverage = {language: set() for language in languages}
    worded = {}
    language_scopes = {}
    appearance_scopes = {}
    digests = {}
    for path in sorted(output.iterdir()):
        if path.suffix.lower() != ".png":
            continue
        match = pattern.fullmatch(path.name)
        if not match:
            raise ValueError(f"Invalid cover filename: {path.name}")
        language, appearance, number = match.groups()
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != COVER_SIZE:
                raise ValueError(f"{path.name} must be a 2010 × 1340 PNG")
            corner = image.crop(CORNER).convert("RGBA")
            dominant = Counter(corner.get_flattened_data()).most_common(1)[0][0]
            difference = ImageChops.difference(
                corner, Image.new("RGBA", corner.size, dominant)
            )
            if any(high > CORNER_TOLERANCE for _, high in difference.getextrema()):
                raise ValueError(f"{path.name} has artwork in the language-pill corner")

        digests[path.name] = sha256(path.read_bytes()).hexdigest()
        language_scopes.setdefault(number, set()).add(language)
        appearance_scopes.setdefault((language, number), set()).add(appearance)
        covered_appearances = {"light", "dark"} if appearance is None else {appearance}
        for covered_language in languages if language is None else {language}:
            coverage[covered_language].update(covered_appearances)
        if language is not None:
            worded.setdefault((appearance, number), set()).add(language)

    for number, scopes in language_scopes.items():
        if None in scopes and len(scopes) > 1:
            raise ValueError(f"Ambiguous language scope for cover {number}")
    for (language, number), scopes in appearance_scopes.items():
        if None in scopes and len(scopes) > 1:
            raise ValueError(
                f"Ambiguous appearance scope for {language or 'all languages'} cover {number}"
            )

    for (appearance, number), present in worded.items():
        if missing := languages - present:
            raise ValueError(
                f"Worded cover {appearance}-{number} missing languages: {', '.join(sorted(missing))}"
            )
    for language, appearances in sorted(coverage.items()):
        if missing := {"light", "dark"} - appearances:
            raise ValueError(
                f"{language} missing cover appearances: {', '.join(sorted(missing))}"
            )

    numbers = sorted(map(int, language_scopes))
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Cover numbers must run consecutively from 1")

    return digests


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    try:
        rendered = verify(args.output)
        if args.compare is not None and rendered != verify(args.compare):
            raise ValueError("Independent build changed the cover PNGs")
        print(f"Verified {len(rendered)} cover PNGs")
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
