from rich import print
from app.agent import handle_user_message, execute_confirmed_command

def main():
    print("[bold cyan]ARIs Phase 1.1[/bold cyan] - hardened tool-calling")
    print("Type 'exit' to quit.\n")

    pending_command = None

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("ARIs: Goodbye 👋")
            break

        if pending_command:
            if user_input.lower() == "yes":
                print("ARIs:", execute_confirmed_command(pending_command), "\n")
            elif user_input.lower() == "no":
                print("ARIs: ✅ Command cancelled.\n")
            else:
                print("ARIs: Please answer yes/no.\n")
                continue
            pending_command = None
            continue

        result = handle_user_message(user_input)
        print("ARIs:", result["message"], "\n")

        if result["type"] == "confirm":
            pending_command = result["command"]

if __name__ == "__main__":
    main()