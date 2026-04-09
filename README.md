# AI Debugging Assistant Agent

A small AI-powered debugging assistant that analyzes error messages, asks one clarification question when needed, and returns structured debugging insights.

## Features

- analyzes error messages and short log snippets
- asks a natural follow-up question when context is missing
- classifies the issue by type, severity, and category
- extracts useful debugging signals
- returns possible causes, next steps, confidence, and reasoning signals

## Example

**Input**
```text
Request timed out after 30 seconds while calling billing service
```
**Agent question**
```text
Is this timeout happening consistently or just occasionally?
```
**User answer**
```text
not sure
```
**Output**

    "summary": "The billing service call timed out after 30 seconds, indicating a high-severity timeout issue likely caused by service unresponsiveness or network delays.",
    "possible_causes": [
        "The billing service is experiencing high latency or is unresponsive.",
        "Network issues are causing delayed communication with the billing service.",
        "Timeout configuration might be too low for current service load.",
        "Downstream service outages or slowdowns are impacting billing service response times."
    ],
    "confidence": "medium",
    "next_steps": [
        "Identify which dependency within the billing service or network path is slow or unresponsive.",
        "Review and potentially increase the timeout configuration values for billing service calls.",
        "Check monitoring and metrics for recent latency spikes or failures in the billing service and related downstream components.",
        "Confirm if retries are configured and being triggered, and evaluate their impact."
    ],
    "based_on_signals": "The clear timeout error mentioning the billing service supports a timeout-related diagnosis. However, the user's uncertainty about the context lowers confidence, requiring further investigation."

## How it works
```text
User input
→ clarification question if needed
→ local tool execution
→ final AI reasoning
→ structured JSON output
```
## Local tools

`classify_error(error_text)` - returns error type, severity, and category

`extract_signals(text)` - extracts keywords, exception names, filenames, and stack trace clues

`investigation_checklist(category)` - returns suggested debugging steps for the issue type

## Tech stack
* Python
* OpenAI API
* CLI interface

## Run locally
1. Install dependencies:
`pip install -r requirements.txt`
2. Create a `.env` file:
`OPENAI_API_KEY=your_api_key_here`
3. Run the app:
`python -m app.main`

## Notes
This project uses a hybrid design:

* local tools run deterministically
* the AI is used for clarification and final reasoning

That makes the behavior easier to understand and debug than a fully autonomous agent.

## Future improvements
* web UI
* Java / Spring Boot version
* larger log ingestion
* smarter cause ranking