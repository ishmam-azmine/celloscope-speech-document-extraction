# Test Data

This directory contains the test data selected for the take-home exercise.

No real patient information is included in this repository.

## Audio

### `audio/english_sample.m4a`

A short English recording created specifically for this assessment.

The corresponding ground-truth transcript is stored in:

`transcripts/english_sample.txt`

It provides a simple English baseline for transcription.

### `audio/bengali_sample.m4a`

A short Bengali recording created specifically for this assessment.

The corresponding ground-truth transcript is stored in:

`transcripts/bengali_sample.txt`

It verifies Bengali transcription support separately from English.

### `audio/no_speech_sample.m4a`

A short recording containing no intentional speech, created specifically for this assessment.

It tests the no-speech / ambient-noise case required by the brief. The chosen API behavior for a confirmed no-speech result is an empty transcript rather than invented speech.

## Lab Report Documents

The lab-report samples are fully synthetic and contain no real patient information.

### `documents/lab_report_clean.png`

A controlled synthetic English-language lab report used as the clean OCR baseline.

Its source text is stored in:

`documents/lab_report_source.txt`

The report deliberately includes formats mentioned in the assignment, including:

- decimal values
- `<0.5`
- comma-separated numbers such as `12,500`
- `gm/dl` and `mg/dL`
- scientific notation
- `10^3/µL`
- reference ranges
- an abnormal-result flag

### `documents/lab_report_challenging.png`

A degraded version of the same synthetic report.

It is rotated, darkened, and imperfectly cropped to approximate some of the photographed-document conditions described in the assignment.

It is intended to expose OCR sensitivity to perspective/orientation, poor lighting, and incomplete framing.

### `documents/non_lab.png`

A synthetic shopping-list document that is intentionally not a medical lab report.

Its source text is stored in:

`documents/non_lab_source.txt`

It tests whether the document endpoint degrades gracefully instead of inventing laboratory results.

## Mock Responses

`mock_responses/` contains deterministic disk-backed provider responses used by the mock adapters and automated tests.

They allow the service and Docker configuration to run without API credentials or model downloads.

The mock responses are not presented as measurements of real-provider accuracy.