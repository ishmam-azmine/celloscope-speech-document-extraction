# Speech & Document Extraction API

A FastAPI service providing:

1. Bengali and English speech transcription
2. Structured extraction of English medical laboratory reports from images

The project uses a layered, provider-based architecture so the service can run deterministically with mock providers while also supporting real AI integrations.

---

## Quick Start

The recommended way to run the project is Docker.

From the repository root:

```bash
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

The Docker configuration uses mock providers by default.

Therefore, a clean clone can start without:

- API credentials
- external AI services
- model downloads
- local GPU requirements

---

# API Endpoints

## 1. Speech Transcription

```text
POST /api/v1/transcribe
```

Multipart form fields:

- `file` — audio file
- `language` — `bn`, `en`, or `auto`

Supported audio MIME types include:

- MP3
- WAV
- M4A / MP4 audio

Audio files larger than 25 MB are rejected.

Example response:

```json
{
  "transcript": "Hello, this is a sample transcription.",
  "detected_language": "en",
  "duration_seconds": 3.2,
  "provider": "mock"
}
```

For a confirmed no-speech result, the service returns an empty transcript instead of inventing speech:

```json
{
  "transcript": "",
  "detected_language": "en",
  "duration_seconds": 4.0,
  "provider": "mock"
}
```

---

## 2. Laboratory Report Extraction

```text
POST /api/v1/documents/extract
```

Multipart form fields:

- `file` — JPEG, PNG, or WebP laboratory-report image

Example response:

```json
{
  "meta": {
    "patient_name": "John Doe",
    "age": "35",
    "sex": "Male",
    "report_date": "2026-08-01",
    "lab_name": "Example Diagnostic Center",
    "reference_no": "LAB-001"
  },
  "results": [
    {
      "test_name": "Glucose",
      "value": 95.0,
      "unit": "mg/dL",
      "reference_range": "70-100",
      "flag": null,
      "raw_line": "Glucose 95 mg/dL 70-100"
    }
  ],
  "unparsed_lines": []
}
```

Every parsed result contains a numeric `value`.

The exact OCR line used for each result is retained in `raw_line`.

OCR lines that cannot be confidently parsed are preserved verbatim in `unparsed_lines` rather than guessed or silently discarded.

If no valid laboratory results can be identified, the endpoint returns HTTP 422 instead of generating fabricated results.

---

# Architecture

The application is divided into three main layers:

```text
app/
├── api/
├── services/
└── adapters/
```

The dependency direction is:

```text
API
 ↓
Services / domain contracts
 ↑
Adapters
```

## `api/`

Responsible for:

- HTTP routes
- uploads
- request validation
- response models
- HTTP error mapping

FastAPI-specific objects stay in this layer.

## `services/`

Responsible for:

- application/business logic
- provider contracts
- laboratory parsing
- date normalization
- numeric and unit normalization
- transcription result handling

The service layer does not import FastAPI, adapters, or provider SDKs.

## `adapters/`

Responsible for external provider integrations.

Current transcription implementations:

- `MockTranscriptionProvider`
- `GroqTranscriptionProvider`

Current OCR implementations:

- `MockOCRProvider`
- `GeminiOCRProvider`

Both mock and real adapters implement the contracts defined in:

```text
app/services/ports.py
```

Provider SDK imports are isolated inside the adapter layer.

This structure allows providers to be replaced without changing the public API or core business logic.

---

# Provider Configuration

Configuration is loaded through a typed Pydantic settings object.

The default configuration is:

```env
TRANSCRIPTION_PROVIDER=mock
OCR_PROVIDER=mock
```

Available transcription providers:

```text
mock
groq
```

Available OCR providers:

```text
mock
gemini
```

Example real-provider configuration:

```env
TRANSCRIPTION_PROVIDER=groq
GROQ_API_KEY=your-key

OCR_PROVIDER=gemini
GEMINI_API_KEY=your-key
```

See:

```text
.env.example
```

for all supported settings.

Real secrets belong only in `.env`.

`.env` is excluded from both Git and the Docker build context.

---

# Laboratory Value Normalization

The service keeps a numeric canonical `value` for parsed laboratory results while preserving the exact original OCR text in `raw_line`.

Examples:

```text
12.5        → 12.5
12,500      → 12500.0
<0.5        → 0.5
1.2 × 10^3  → 1200.0
```

For qualified values such as `<0.5`, the numeric component can be normalized while the original qualified representation remains recoverable from `raw_line`.

Common equivalent unit spellings are normalized.

Examples:

```text
gm/dl     → g/dL
g/dl      → g/dL
mg/dl     → mg/dL
mmol/l    → mmol/L
10^3/uL   → 10^3/µL
```

Reference-range separators are normalized where confidently recognized.

Examples:

```text
0.8 - 1.2
0.8 – 1.2
0.8 to 1.2
```

become:

```text
0.8-1.2
```

Dates are normalized to:

```text
YYYY-MM-DD
```

only when their interpretation is unambiguous.

Examples:

```text
August 8, 2026 → 2026-08-08
13/08/2026     → 2026-08-13
08/13/2026     → 2026-08-13
```

Ambiguous dates such as:

```text
08/09/2026
```

are preserved verbatim instead of guessed.

The parser follows a conservative rule:

> If a value or line cannot be confidently interpreted, preserve it rather than inventing information.

---

# Validation and Error Handling

The API intentionally handles cases including:

- unsupported audio formats
- unsupported document formats
- empty audio files
- empty document files
- audio larger than 25 MB
- invalid language values
- missing provider credentials
- transcription-provider failures
- OCR-provider failures
- silence / no speech
- documents containing no valid laboratory results

External provider failures are converted into structured API errors rather than exposing provider stack traces.

---

# Test Data

Test data is stored under:

```text
testdata/
```

A detailed description of the source and purpose of each fixture is available in:

```text
testdata/README.md
```

No real patient information is included.

## Speech fixtures

The repository includes:

```text
testdata/audio/english_sample.m4a
testdata/audio/bengali_sample.m4a
testdata/audio/no_speech_sample.m4a
```

Reference transcripts are stored in:

```text
testdata/transcripts/english_sample.txt
testdata/transcripts/bengali_sample.txt
testdata/transcripts/no_speech_sample.txt
```

The no-speech reference transcript is intentionally empty.

These samples were selected to provide:

- an English baseline
- a Bengali baseline
- a no-speech / ambient-noise edge case

## Document fixtures

The laboratory-report images are fully synthetic.

Included samples:

```text
testdata/documents/lab_report_clean.png
testdata/documents/lab_report_challenging.png
testdata/documents/non_lab.png
```

`lab_report_clean.png` provides known ground truth and deliberately includes challenging formats such as:

- `<0.5`
- comma-separated values
- multi-word test names
- `gm/dl`
- scientific notation
- `10^3/µL`
- spaced reference ranges
- an abnormal-result flag

`lab_report_challenging.png` is a rotated, darkened, and imperfectly cropped version of the synthetic report. It is intended to expose weaknesses in OCR under photographed-document conditions.

`non_lab.png` is intentionally not a medical report and is used to verify graceful rejection instead of fabricated medical output.

---

# Automated Tests

Install dependencies and run:

```bash
pytest -q
```

The test suite covers:

- English transcription
- Bengali transcription
- Groq language-name normalization
- invalid languages
- unsupported audio
- empty audio
- audio over 25 MB
- no-speech behavior
- transcription-provider failure handling
- transcription-provider selection
- document extraction
- unsupported document formats
- empty documents
- non-lab documents
- raw OCR preservation
- unparsed OCR preservation
- numeric normalization
- unit normalization
- reference-range normalization
- date normalization
- ambiguous-date preservation
- scientific notation
- multi-word test names
- abnormal-result flags
- OCR-provider selection

At the time of submission, the suite contains 34 passing tests.

---

# Local Development

Python 3.11 or newer is required.

Create a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# Known Limitations

- OCR quality still depends on how much readable text the selected OCR provider can recover from severely blurred, cropped, or poorly illuminated images.
- The laboratory parser intentionally favors precision over guessing, so unfamiliar report layouts may produce entries in `unparsed_lines`.
- The parser currently targets English laboratory reports as required by the task.
- Only common laboratory numeric, unit, range, and date formats are normalized; unknown or ambiguous formats are preserved rather than inferred.
- The default mock providers are deterministic fixtures and are not measurements of real-provider accuracy.
- Real Groq and Gemini modes require network access and valid credentials.
- Provider responses can vary over time because external model behavior is outside this application's control.

---

# Repository Structure

```text
app/
├── adapters/
│   ├── ocr/
│   └── transcription/
├── api/
├── services/
│   ├── ports.py
│   ├── date_normalizer.py
│   └── ...
├── config.py
└── main.py

tests/

testdata/
├── audio/
├── documents/
├── mock_responses/
├── transcripts/
└── README.md

Dockerfile
compose.yaml
requirements.txt
.env.example
README.md
DECISIONS.md
```

---

# Security

No API keys or other credentials are stored in the repository.

Secrets are provided through environment variables and local `.env` files.

The committed `.env.example` contains only configuration names and safe defaults.