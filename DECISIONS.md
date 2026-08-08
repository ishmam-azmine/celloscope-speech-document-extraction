# Engineering Decisions

## 1. Mock providers are the default runtime

**Chosen:** Use deterministic mock transcription and OCR providers by default.

**Rejected:** Require external APIs or locally downloaded models for normal startup.

**Why:** A clean clone should run without credentials, network-dependent AI calls, GPU requirements, or model downloads. Disk-backed mock responses make local execution and automated evaluation deterministic while preserving the same provider boundaries used by real integrations.

---

## 2. Real model choices: Whisper Large V3 and Gemini 2.5 Flash

**Chosen:** Use Groq-hosted `whisper-large-v3` for real speech transcription and `gemini-2.5-flash` for real document OCR.

**Rejected:** Self-hosted speech/OCR models as the default real path, and asking the OCR model to directly produce final structured laboratory JSON.

**Why:** The selected hosted models keep setup lightweight while still demonstrating a real provider path. `whisper-large-v3` supports multilingual transcription needed for Bengali and English. Gemini is used only to recover visible document text, while parsing and normalization remain deterministic application logic. Self-hosting would add model downloads, hardware requirements, and setup complexity without improving the architectural goals of this exercise.

---

## 3. Provider contracts live in the service layer

**Chosen:** Define the transcription and OCR contracts once in `app/services/ports.py`, with adapters implementing those contracts.

**Rejected:** Maintain separate provider interfaces inside each adapter package.

**Why:** This keeps dependencies pointing inward and gives the application a single provider boundary. Services depend only on their own contracts, while provider-specific implementations remain replaceable.

---

## 4. Preserve uncertain OCR instead of guessing

**Chosen:** Only create a structured laboratory result when a numeric result can be parsed confidently. Preserve other OCR lines verbatim in `unparsed_lines`.

**Rejected:** Infer missing values, units, ranges, dates, or test names from ambiguous text.

**Why:** Incorrectly inventing medical information is worse than returning partially structured data. The API therefore favors conservative extraction and traceability. Ambiguous dates are also preserved instead of guessed.

Each successfully parsed result retains its exact source OCR line in `raw_line`.

---

## 5. Normalize for downstream use while retaining source text

**Chosen:** Convert recognized values, units, reference ranges, and unambiguous dates into canonical forms while preserving the original OCR text.

Examples include:

- `12,500` → numeric `12500.0`
- `1.2 × 10^3` → numeric `1200.0`
- `gm/dl` → `g/dL`
- `mg/dl` → `mg/dL`
- `0.8 - 1.2` → `0.8-1.2`
- `August 8, 2026` → `2026-08-08`

**Rejected:** Either expose only raw OCR text or destructively replace it with normalized data.

**Why:** Canonical values are easier for downstream systems to consume, while `raw_line` and preserved ambiguous content provide traceability and reduce information loss.