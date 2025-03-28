import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ui.enron_shell import EnronMailShell


def main():
    maildir_path = "./maildir"
    max_emails = 5000

    # Handle args manually
    args = sys.argv[1:]

    if "--help" in args:
        print("Usage: python main.py [--max_emails N]")
        sys.exit(0)

    if "--max_emails" in args:
        try:
            idx = args.index("--max_emails")
            max_emails = int(args[idx + 1])
        except (IndexError, ValueError):
            print("❌ Invalid usage of --max_emails. Example: --max_emails 10000")
            sys.exit(1)

    if not os.path.exists(maildir_path):
        print(f"❌ Error: Enron dataset directory '{maildir_path}' not found.")
        print(
            "Please download the Enron dataset by running './scripts/download_enron.sh' "
            "or for Windows, 'download_enron.cmd'"
        )
        sys.exit(1)

    shell = EnronMailShell(maildir_path, max_emails)
    shell.run()


if __name__ == "__main__":
    main()
