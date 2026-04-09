import json
from app.agent import analyze_error


def main():
    print("Paste your error (type 'exit' to quit):")

    while True:
        user_input = input("\n> ")

        if user_input.lower() == "exit":
            break

        result = analyze_error(user_input)
        print("\n--- AI RESPONSE ---")

        try:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=2))
        except Exception:
            print(result)


if __name__ == "__main__":
    main()