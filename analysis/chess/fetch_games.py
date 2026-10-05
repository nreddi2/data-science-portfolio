from pathlib import Path
import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone

import requests
import zstandard

SOURCE = "https://database.lichess.org/standard/lichess_db_standard_rated_2026-09.pgn.zst"
LIMIT = 30000
STRIDE = 10
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


def collect_games():
    rows, players = [], {}
    scanned = 0
    tag_pattern = re.compile(r'^\[(\w+) "(.*)"\]$')

    def player_id(name):
        if not name or name == "?":
            return ""
        key = name.casefold()
        if key not in players:
            players[key] = f"p{len(players) + 1:06d}"
        return players[key]

    with requests.get(SOURCE, stream=True, timeout=(20, 90)) as response:
        response.raise_for_status()
        with zstandard.ZstdDecompressor().stream_reader(response.raw) as stream:
            text_stream = io.TextIOWrapper(stream, encoding="utf-8")
            tags = {}
            for line in text_stream:
                match = tag_pattern.match(line.strip())
                if match:
                    tags[match[1]] = match[2]
                elif not line.strip() and tags:
                    scanned += 1
                    if scanned % STRIDE:
                        tags = {}
                        continue
                    site = tags.get("Site", "")
                    rows.append({
                        "source_row": scanned,
                        "game_id": hashlib.sha256(site.encode()).hexdigest()[:20] if site else "",
                        "event": tags.get("Event", ""),
                        "date": tags.get("UTCDate", ""),
                        "time": tags.get("UTCTime", ""),
                        "white_rating": tags.get("WhiteElo", ""),
                        "black_rating": tags.get("BlackElo", ""),
                        "white_title": tags.get("WhiteTitle", ""),
                        "black_title": tags.get("BlackTitle", ""),
                        "white_player": player_id(tags.get("White", "")),
                        "black_player": player_id(tags.get("Black", "")),
                        "time_control": tags.get("TimeControl", ""),
                        "result": tags.get("Result", ""),
                        "variant": tags.get("Variant", "Standard"),
                    })
                    tags = {}
                    if len(rows) % 5000 == 0:
                        print(f"Collected {len(rows):,} sampled headers", flush=True)
                    if len(rows) == LIMIT:
                        break
    if len(rows) != LIMIT:
        raise ValueError("The download ended before the requested sample was collected.")

    path = DATA / "games_raw.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "source": SOURCE,
        "source_page": "https://database.lichess.org/",
        "license": "CC0",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "sampling": "Every tenth complete PGN header block among the first 300000, before filtering. A systematic sample of an archive prefix, not a random sample of the month.",
        "source_headers_scanned": scanned,
        "raw_rows": len(rows),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "privacy": "Player names replaced with within-sample IDs; game URLs replaced with hashes. These are pseudonyms, not a guarantee of anonymity.",
        "exclusions_at_collection": "Moves, opening, ECO, termination, rating changes, and original player names were not saved.",
    }
    (DATA / "source.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved {len(rows):,} game headers to {path}")


if __name__ == "__main__":
    collect_games()
