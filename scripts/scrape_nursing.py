import json
import os
import sys
from pathlib import Path

# Add src to sys.path to allow importing timetable_scrapers if not installed
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from timetable_scrapers import ScraperRegistry
except ImportError as e:
    print(f"Error: Could not import timetable_scrapers. {e}")
    sys.exit(1)

def main():
    # Configuration
    scraper_name = "nursing_exams"
    # The user can change this to their actual filename
    input_file = "docs/nursing_timetable_jan26.xlsx"
    output_dir = "uploads/nursing/outputs"
    output_file = os.path.join(output_dir, "nursing_exams_jan26.json")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print(f"Please place your nursing excel file at '{input_file}' or update the script.")
        # Try to find any xlsx file in docs if the default is missing
        xlsx_files = list(Path("docs").glob("*.xlsx"))
        if xlsx_files:
            print(f"Found other xlsx files in docs/: {[f.name for f in xlsx_files]}")
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
    try:
        with open(input_file, "rb") as f:
            entries = scraper.extract(f)
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)

    print(f"Extracted {len(entries)} entries.")

    # Convert to dictionaries for JSON serialization
    data = [entry.to_dict() for entry in entries]

    print(f"Saving to: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Success!")

if __name__ == "__main__":
    main()
