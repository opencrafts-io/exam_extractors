# Timetable Scrapers
Python package for scraping exam timetables.

## Overview
This provides a plugin-based architecture for extracting timetable data from excel files.
Each institution has its own implementation, ensuring maintanability and extensibility.

### Key Features
- `Plugin Architecture`: Easy to add new institution scrapers.
- `Standardized Output`: All scrapers return the samde data structure
- `Type Safe`: Uses dataclassases and type hints
- `Extensible`: Base class provides common functionality
- `Independent`: Can be used in multiple projects

## Installation
cd timetable-scrapers
pip install -e .
pip install -e ".[dev]"

### Production (soon)
pip install timetable-scrapers

## Usage

### Basic Usage

```python
from timetable_scrapers import ScraperRegistry

# Get a scraper instance
scraper = ScraperRegistry.get_scraper("nursing_exams")

# Extract data from file
with open("timetable.xlsx", "rb") as f:
    courses = scraper.extract(f)

# courses is a list of CourseEntry objects
for course in courses:
    print(f"{course.course_code} at {course.venue} on {course.day}")
```

### Available Scrapers

- `nursing_exams`: Nursing exam timetable
- `strath`: Strathmore University timetable
- `kca`: KCA University exam timetable
- `Daystar`: Daystar exam timetable

### List Available Scrapers

```python
from timetable_scrapers import ScraperRegistry

available = ScraperRegistry.list_scrapers()
print(available)  # ['nursing_exams', 'strath', 'kca', 'school_exams']
```

### Converting to Dictionary

```python
from timetable_scrapers import ScraperRegistry, CourseEntry

scraper = ScraperRegistry.get_scraper("kca")
courses = scraper.extract(file)

# Convert to dictionaries for JSON serialization
course_dicts = [course.to_dict() for course in courses]
```

### Professor API Integration

To send scraped data to the Professor API, use `build_ingest_payload()` which creates contract-compliant payloads:

```python
from timetable_scrapers import ScraperRegistry, build_ingest_payload, get_institution_id

# Extract data
scraper = ScraperRegistry.get_scraper("nursing_exams")
with open("timetable.xlsx", "rb") as f:
    entries = scraper.extract(f)

# Get stable institution ID
institution_id = get_institution_id("nursing_exams")

# Build contract-compliant payload
payloads = build_ingest_payload(
    institution_id=institution_id,
    semester_id=12,
    entries=entries,
)

# Send to Professor API
import requests
for payload in payloads:
    response = requests.post(
        "https://professor.example.com/api/exams/ingest/",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer <token>"
        }
    )
    print(f"Created: {response.json()['created']}, Updated: {response.json()['updated']}")
```

**Key features:**
- Automatically parses structured `exam_date`, `start_time`, `end_time` from free-form `day`/`time` strings
- Removes `datetime_str` from items (moves to `raw_data` if present)
- Deduplicates entries by `(institution_id, semester_id, course_code)` with last-wins policy
- Optionally chunks large batches: `build_ingest_payload(..., chunk_size=5000)`

## Architecture

### Package Structure

```
timetable_scrapers/
├── base/              # Base classes and interfaces
├── utils/             # Shared utilities
├── scrapers/          # Institution-specific scrapers
│   ├── nursing/
│   ├── strath/
│   ├── kca/
│   └── school/
├── registry.py        # Scraper registry/factory
└── schemas.py         # Data models
```

### Design Patterns

- **Strategy Pattern**: Each institution is a strategy (scraper class)
- **Factory Pattern**: Registry creates scraper instances
- **Plugin Pattern**: Scrapers register themselves automatically

### Adding a New Scraper

1. Create a new directory under `scrapers/`
2. Create scraper class inheriting from `BaseTimetableScraper`
3. Implement `institution_name` property and `extract()` method
4. Register with `@ScraperRegistry.register("name")`
5. Import in `scrapers/__init__.py`

Example:

```python
from ...base.scraper import BaseTimetableScraper
from ...registry import ScraperRegistry
from ...schemas import CourseEntry

@ScraperRegistry.register("new_institution")
class NewInstitutionScraper(BaseTimetableScraper):
    @property
    def institution_name(self) -> str:
        return "new_institution"

    def extract(self, file) -> List[CourseEntry]:
        # Your extraction logic here
        return []
```

## Data Structure

All scrapers return `CourseEntry` objects with the following fields:

- `course_code` (str): Course code (required)
- `day` (str): Day/date string
- `time` (str): Time string (e.g., "8:00AM-10:00AM")
- `venue` (str): Venue/room name
- `campus` (str): Campus name
- `coordinator` (str): Coordinator name
- `hrs` (str): Duration in hours
- `invigilator` (str): Invigilator name
- `datetime_str` (str, optional): ISO format datetime
- `course_name` (str): Full course name
- `raw_data` (dict): Institution-specific data

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
ruff check src/
```

## License

MIT

## Contributing

When adding a new institution scraper:

1. Follow the existing scraper structure
2. Implement all abstract methods
3. Add tests for your scraper
4. Update this README with the new scraper name
