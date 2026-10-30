import argparse
from pathlib import Path

from .report import run


def main():
    parser = argparse.ArgumentParser(
        description="Reproduce five maintenance SQL decisions from synthetic data"
    )
    parser.add_argument("--output", type=Path, default=Path("reports"))
    parser.add_argument("--start", default="2025-01-01 00:00:00")
    parser.add_argument("--end", default="2025-04-01 00:00:00")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--save-db",
        type=Path,
        help="Optional NEW database path; existing files are preserved",
    )
    args = parser.parse_args()
    try:
        result = run(args.output, args.start, args.end, args.seed, args.save_db)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    print(
        f"Report: {args.output / 'index.html'}; SQLite {result['sqlite']}; synthetic seed {args.seed}"
    )


if __name__ == "__main__":
    main()
