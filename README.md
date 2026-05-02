# Timetable Scrapers

A lightweight, plugin-based Python package for scraping exam timetables and serving the **Academia.io Professor** feature. This tool provides the essential exam schedule data for the Academia mobile app.

## Overview

This project extracts exam schedules from various institution formats (Excel, CSV, etc.) and transforms them into a minimal, standardized format required by the Professor API.

### Key Features
- **Plugin Architecture**: Easily add new institution scrapers by inheriting from `BaseTimetableScraper`.
- **Minimal Schema**: Strictly adheres to the essential fields required for mobile app consumption.
- **ISO 8601 UTC**: All temporal data is normalized to UTC ISO 8601 strings.

---

## Quick Start for New Users

If you are new to the project or have just forked it, follow these steps to run your own scripts and output JSON files.

### 1. Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/your-username/exam_timetable_extractors.git
cd exam_timetable_extractors
pip install -e .
```

### 2. Running Scrapers

You can create a simple script to intake an Excel file and output a JSON file.

```python
import json
from timetable_scrapers import ScraperRegistry

# 1. Get the scraper for your institution
scraper = ScraperRegistry.get_scraper("nursing_exams")

# 2. Extract data from the Excel file
with open("path/to/your/timetable.xlsx", "rb") as f:
    entries = scraper.extract(f)

# 3. Convert entries to dictionaries
data = [entry.to_dict() for entry in entries]

# 4. Save to JSON
with open("output_timetable.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Successfully extracted {len(data)} exam entries.")
```

### 3. Adding a New Institution Scraper

To add a new institution:
1. Create a new directory in `src/timetable_scrapers/scrapers/`.
2. Create a `scraper.py` file.
3. Inherit from `BaseTimetableScraper` and implement `extract`.
4. Register it: `@ScraperRegistry.register("your_institution_id")`.
5. Import it in `src/timetable_scrapers/scrapers/__init__.py`.

---

## Professor API Data Contract

All scrapers must output data matching this minimal contract.

### Data Model (`CourseEntry`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `course_code` | string | ✓ | Course identifier (e.g., "CS101"). |
| `start_time` | string | ✓ | ISO 8601 UTC datetime (e.g., "2026-04-28T08:00:00Z"). |
| `end_time` | string | ✓ | ISO 8601 UTC datetime (e.g., "2026-04-28T10:00:00Z"). |
| `venue` | string | ✓ | Exam venue/location. |
| `coordinator` | string | ✗ | Optional: Exam coordinator name. |
| `hrs` | string | ✗ | Optional: Duration (e.g., "2 hours"). |
| `raw_data` | object | ✗ | Store all original/extra data here for auditing. |

### Time Normalization

The system uses `src/timetable_scrapers/utils/time_parser.py` to convert institution-specific date/time strings into UTC ISO 8601.

```python
from timetable_scrapers.utils.time_parser import parse_exam_datetime

# Converts local "28/04/2026" and "8:30AM" to UTC ISO string
iso_time = parse_exam_datetime("28/04/2026", "8:30AM", timezone_str="EAT")
# Result: "2026-04-28T05:30:00Z"
```

---

## Professor API Ingestion

To ingest data into the Professor API:

```python
from timetable_scrapers import ScraperRegistry, build_ingest_payload, send_to_professor

# 1. Extract
scraper = ScraperRegistry.get_scraper("nursing_exams")
with open("timetable.xlsx", "rb") as f:
    entries = scraper.extract(f)

# 2. Build Payload
payloads = build_ingest_payload(
    institution_id="nursing_school_001",
    entries=entries,
    semester_id=12
)

# 3. Send to API
results = send_to_professor(
    payloads,
    api_url="https://professor-api.example.com/exams/ingest/",
    api_token="your_auth_token"
)
```

---

## Development & Testing

### Running Tests
```bash
pytest tests/
```

### Formatting
```bash
black src/
```