import json
import os
import sys
from pathlib import Path

# Add src to sys.path to allow importing timetable_scrapers if not installed
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from timetable_scrapers import ScraperRegistry
except ImportError as e:
    print(f"Error: Could not import timetable_scrapers. {e}")
    sys.exit(1)

def main():
    scraper_name = "strath"
    input_file = "docs/strath_april_draft.xlsx"
    output_file = "uploads/strath/outputs/strath_april_draft_2.json"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    print(f"Loading scraper: {scraper_name}")
    try:
        scraper = ScraperRegistry.get_scraper(scraper_name)
    except ValueError as e:
        print(f"Error: {e}")
        available = ScraperRegistry.list_scrapers()
        print(f"Available scrapers: {available}")
        sys.exit(1)

    print(f"Extracting data from: {input_file}")
    with open(input_file, "rb") as f:
        entries = scraper.extract(f)

    print(f"Extracted {len(entries)} entries.")

    data = [entry.to_dict() for entry in entries]

    print(f"Saving to: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Success!")

if __name__ == "__main__":
    main()