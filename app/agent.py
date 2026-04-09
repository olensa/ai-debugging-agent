import json
from openai import OpenAI

from app.config import OPENAI_API_KEY
from app.tools import classify_error, extract_signals, investigation_checklist

client = OpenAI(api_key=OPENAI_API_KEY)


TOOLS = [
    {
        "type": "function",
        "name": "classify_error",
        "description": "Classify an error into type, severity, and category based on raw error text.",
        "parameters": {
            "type": "object",
            "properties": {
                "error_text": {
                    "type": "string",
                    "description": "The raw error text or log snippet."
                }
            },
            "required": ["error_text"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "extract_signals",
        "description": "Extract useful debugging signals such as stack trace lines, filenames, method names, exception names, and keywords.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The raw error text or stack trace."
                }
            },
            "required": ["text"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "investigation_checklist",
        "description": "Return investigation steps for a given debugging category.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "A debugging category such as null_reference, timeout, database, auth, validation, network, or unknown."
                }
            },
            "required": ["category"],
            "additionalProperties": False
        }
    }
]


def run_tool(tool_name: str, arguments: dict) -> dict:
    if tool_name == "classify_error":
        return classify_error(arguments["error_text"])
    if tool_name == "extract_signals":
        return extract_signals(arguments["text"])
    if tool_name == "investigation_checklist":
        return investigation_checklist(arguments["category"])

    raise ValueError(f"Unknown tool: {tool_name}")

def clean_output(text: str) -> str:
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json\n", "")
    return text.strip()

def analyze_error(error_text: str) -> str:
    # STEP 1: decide whether to ask one clarification question
    decision_response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a senior backend engineer debugging an issue. "
                    "Decide if you need more information before giving a final answer. "
                    "If yes, ask ONE short, natural, human-friendly question like a senior developer talking to a teammate. "
                    "Avoid formal or long phrasing. Keep it conversational and practical. "
                    "If no, say ONLY 'FINAL'."
                ),
            },
            {
                "role": "user",
                "content": error_text,
            },
        ],
    )

    decision_text = decision_response.output_text.strip()

    if decision_text != "FINAL":
        print("\n[Agent question]")
        print(decision_text)

        user_answer = input("\nYour answer (optional): ").strip()

        if user_answer:
            error_text = f"{error_text}\nAdditional context: {user_answer}"

    # STEP 2: force baseline tools
    classification = classify_error(error_text)
    signals = extract_signals(error_text)
    checklist = investigation_checklist(classification["category"])

    print(f"\n[Forced tool] classify_error → {classification}")
    print(f"[Forced tool] extract_signals → {signals}")
    print(f"[Forced tool] investigation_checklist → {checklist}")

    # STEP 3: enrich context for final reasoning
    enriched_context = f"""
Original error:
{error_text}

Classification:
{json.dumps(classification, indent=2)}

Signals:
{json.dumps(signals, indent=2)}

Checklist:
{json.dumps(checklist, indent=2)}
"""

    # STEP 4: final reasoning call - NO tool calling here
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a senior backend engineer helping debug production issues. "
                    "Use the provided classification, extracted signals, checklist, and user context to produce the final answer. "
                    "Do not call tools or describe tool usage. "
                    "Set confidence to low if user provides vague or uncertain answers like 'not sure'. "
                    "Set confidence to low if missing information, medium if partially inferred, high if clear. "
                    "Return final answer as JSON with keys: "
                    "summary, possible_causes, confidence, next_steps, based_on_signals."
                    "Keep the summary to 1-2 sentences. "
                    "Do not repeat the same idea in multiple ways. "
                    "In based_on_signals, mention if user uncertainty lowered confidence."
                ),
            },
            {
                "role": "user",
                "content": enriched_context,
            },
        ],
    )

    return clean_output(response.output_text)