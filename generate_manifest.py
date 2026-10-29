import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(".")
DATA_DIRS = [Path("data") / "master",
             Path("data") / "transactions",
             Path("data") / "anomalies"]

SEED = 20261022


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def count_csv_rows(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return max(sum(1 for _ in csv.reader(file)) - 1, 0)


def main():
    files = []

    for directory in DATA_DIRS:
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*")):
            if not path.is_file():
                continue

            # Exclude generated metadata and confidential ground-truth labels.
            if path.name in {
                "source_manifest.json",
                "checksums.sha256",
                "ground_truth.csv",
            }:
                continue

            entry = {
                "path": path.as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }

            if path.suffix.lower() == ".csv":
                entry["data_rows"] = count_csv_rows(path)

            files.append(entry)

    manifest = {
        "project": "Loan Decision Engine",
        "seed": SEED,
        "python_version": platform.python_version(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }

    manifest_path = ROOT / "source_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)

    checksum_path = ROOT / "checksums.sha256"
    with checksum_path.open("w", encoding="utf-8") as file:
        for entry in files:
            file.write(f"{entry['sha256']}  {entry['path']}\n")

    print(f"Manifest created: {manifest_path}")
    print(f"Checksum file created: {checksum_path}")
    print(f"Files inventoried: {len(files)}")


if __name__ == "__main__":
    main()
