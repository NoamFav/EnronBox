import os
import subprocess
import email
import sys
from typing import Optional, List, Dict, Any

# Prompt toolkit for advanced CLI
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import the classifier
from src.enron_classifier import EnronEmailClassifier


class EnronMailShell:
    def __init__(self, maildir_path: str = "maildir"):
        self.maildir_path = maildir_path
        self.current_email: Optional[Dict[str, Any]] = None
        self.classifier = EnronEmailClassifier()
        self.console = Console()

        # Style for prompt toolkit
        self.style = Style.from_dict(
            {
                "prompt": "#ansigreen bold",
                "rprompt": "#ansigray italic",
            }
        )

        # Prepare the shell
        self._load_classifier()

    def _load_classifier(self):
        """Load and train the email classifier"""
        try:
            # Load emails and train the model
            email_df, labels = self.classifier.load_enron_emails(
                self.maildir_path, max_emails=5000
            )
            self.classifier.train(email_df, labels)
            self.console.print(
                Panel.fit(
                    Text("✅ Email Classifier Loaded Successfully", style="bold green"),
                    border_style="green",
                )
            )
        except Exception as e:
            self.console.print(
                Panel.fit(
                    Text(f"❌ Failed to load classifier: {e}", style="bold red"),
                    border_style="red",
                )
            )

    def extract_body(self, msg):
        """Extract email body"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(
                        "latin1", errors="ignore"
                    )
        else:
            return msg.get_payload(decode=True).decode("latin1", errors="ignore")
        return ""

    def browse_emails(self) -> Optional[str]:
        """Browse and select emails using fzf"""
        try:
            # First, select user
            users = sorted(os.listdir(self.maildir_path))
            user_cmd = f"echo '{chr(10).join(users)}' | fzf --height 50% --layout=reverse --border"
            user = subprocess.check_output(user_cmd, shell=True, text=True).strip()
            if not user:
                return None

            # Select folder
            folders = sorted(os.listdir(os.path.join(self.maildir_path, user)))
            folder_cmd = f"echo '{chr(10).join(folders)}' | fzf --height 50% --layout=reverse --border"
            folder = subprocess.check_output(folder_cmd, shell=True, text=True).strip()
            if not folder:
                return None

            # Select email
            folder_path = os.path.join(self.maildir_path, user, folder)
            files = sorted(f for f in os.listdir(folder_path) if not f.startswith("."))

            email_cmd = f"echo '{chr(10).join(files)}' | fzf --height 50% --layout=reverse --border"
            email_file = subprocess.check_output(
                email_cmd, shell=True, text=True
            ).strip()
            if not email_file:
                return None

            # Load email
            full_path = os.path.join(folder_path, email_file)
            return full_path

        except subprocess.CalledProcessError:
            # This happens if user cancels fzf selection
            return None
        except Exception as e:
            self.console.print(f"[bold red]Error browsing emails: {e}[/bold red]")
            return None

    def display_email(self, email_path: str):
        """Display email details with rich formatting"""
        try:
            with open(email_path, "r", encoding="latin1", errors="ignore") as f:
                msg = email.message_from_file(f)

            # Extract details
            sender = msg.get("From", "[No sender]")
            subject = msg.get("Subject", "[No subject]")
            body = self.extract_body(msg)[:1000]  # First 1000 chars

            # Prepare email data for AI classification
            email_data = {
                "subject": subject,
                "body": body,
                "sender": sender,
                "has_attachment": len(msg.get_payload()) > 1,
                "num_recipients": len(msg.get_all("To", []))
                + len(msg.get_all("Cc", [])),
                "time_sent": email.utils.parsedate_to_datetime(msg.get("Date")),
            }

            # AI Classification
            prediction = self.classifier.predict(email_data)

            # Create rich display
            table = Table(
                title="Email Details", show_header=True, header_style="bold magenta"
            )
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("From", sender)
            table.add_row("Subject", subject)
            table.add_row(
                "Category",
                f"{prediction['category']} (Confidence: {prediction['confidence']:.2%})",
            )
            table.add_row(
                "Emotional Tone",
                f"Polarity: {prediction['emotion']['polarity']:.2f}, "
                f"Subjectivity: {prediction['emotion']['subjectivity']:.2f}",
            )

            # Body preview
            body_panel = Panel(
                Syntax(body, "txt", theme="monokai", line_numbers=False),
                title="Body Preview",
                border_style="green",
            )

            self.console.print(table)
            self.console.print(body_panel)

            self.current_email = email_data
            return email_data

        except Exception as e:
            self.console.print(f"[bold red]Error displaying email: {e}[/bold red]")
            return None

    def run(self):
        """Main shell loop"""
        session = PromptSession(style=self.style)

        self.console.print(
            Panel.fit(
                Text("🚀 Enron Email Intelligence Shell", style="bold cyan"),
                subtitle="Explore and Analyze Emails with AI",
                border_style="cyan",
            )
        )

        while True:
            try:
                user_input = session.prompt(
                    HTML("<ansicyan>📬 EnronAI > </ansicyan>"),
                    rprompt=HTML("<ansigray>Type :help for options</ansigray>"),
                )

                if user_input.startswith(":"):
                    cmd = user_input[1:].strip().lower()

                    match cmd:
                        case "browse":
                            email_path = self.browse_emails()
                            if email_path:
                                self.display_email(email_path)

                        case "analyze" if self.current_email:
                            prediction = self.classifier.predict(self.current_email)
                            detailed_analysis = f"""
🔍 Detailed Email Analysis:
Category:       {prediction['category']}
Confidence:     {prediction['confidence']:.2%}
Emotional Tone:
  - Polarity:      {prediction['emotion']['polarity']:.2f}
  - Subjectivity:  {prediction['emotion']['subjectivity']:.2f}
"""
                            self.console.print(
                                Panel(
                                    Text(detailed_analysis, style="cyan"),
                                    title="📊 AI Insights",
                                    border_style="green",
                                )
                            )

                        case "help":
                            help_text = """
🌟 Enron Email Intelligence Shell Commands 🌟
:browse   - Browse and select emails
:analyze  - Analyze the currently selected email
:help     - Show this help menu
:quit     - Exit the shell
"""
                            self.console.print(
                                Panel(
                                    Text(help_text, style="green"),
                                    title="💡 Help Menu",
                                    border_style="cyan",
                                )
                            )

                        case "quit":
                            break

                        case _:
                            self.console.print(
                                Panel.fit(
                                    Text(
                                        "❓ Unknown command. Type :help for options",
                                        style="red",
                                    ),
                                    border_style="red",
                                )
                            )

                else:
                    self.console.print(
                        Panel.fit(
                            Text("❗ Invalid input. Use ':' commands", style="yellow"),
                            border_style="yellow",
                        )
                    )

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

        self.console.print(
            Panel.fit(
                Text(
                    "👋 Goodbye! Thanks for using Enron Email Intelligence Shell",
                    style="bold green",
                ),
                border_style="green",
            )
        )


def main():
    maildir_path = "./maildir"  # Update this to your Enron dataset path
    if not os.path.exists(maildir_path):
        print(f"Error: Enron dataset directory '{maildir_path}' not found.")
        print("Please download the Enron dataset from https://www.cs.cmu.edu/~enron/")
        sys.exit(1)

    shell = EnronMailShell(maildir_path)
    shell.run()


if __name__ == "__main__":
    main()
