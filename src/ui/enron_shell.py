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
from rich import box
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import the classifier
from src.enron_classifier import EnronEmailClassifier


class EnronMailShell:
    def __init__(self, maildir_path: str = "maildir", max_emails: int = 5000):
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
        self._load_classifier(max_emails=max_emails)

    def _load_classifier(self, max_emails: int = 5000):
        """Load and train the email classifier"""
        try:
            # Load emails and train the model
            email_df, labels = self.classifier.load_enron_emails(
                self.maildir_path, max_emails=max_emails
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
                "recipients": msg.get_all("To", []) + msg.get_all("Cc", []),
                "time_sent": email.utils.parsedate_to_datetime(msg.get("Date")),
            }

            # AI Classification
            prediction = self.classifier.predict(email_data)

            # Create rich display
            table = Table(
                title="📧 Email Details",
                title_style="bold green",
                show_header=True,
                header_style="bold white on dark_magenta",
                box=box.ROUNDED,
                pad_edge=False,
                expand=False,
                row_styles=["none", "dim"],
            )

            table.add_column("🔖 Field", style="cyan", no_wrap=True)
            table.add_column("📝 Value", style="white")

            table.add_row("📤 From", sender)
            table.add_row(
                "📥 Recipients",
                ", ".join(email_data["recipients"]) or "[No recipients]",
            )
            table.add_row("📅 Sent", str(email_data["time_sent"]))
            table.add_row("📝 Subject", subject)
            table.add_row(
                "🏷️ Category",
                f"{prediction['category']} (Confidence: {prediction['confidence']:.2%})",
            )
            table.add_row(
                "🎭 Emotional Tone",
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

    def user_stats(self):
        """Display email statistics for a selected user"""
        try:
            # Step 1: Pick user
            users = sorted(os.listdir(self.maildir_path))
            user_cmd = f"echo '{chr(10).join(users)}' | fzf --height 50% --layout=reverse --border"
            user = subprocess.check_output(user_cmd, shell=True, text=True).strip()
            if not user:
                return

            user_path = os.path.join(self.maildir_path, user)
            if not os.path.isdir(user_path):
                self.console.print(
                    Panel.fit(
                        Text(f"❌ Invalid user folder: {user_path}", style="bold red"),
                        border_style="red",
                    )
                )
                return

            # Step 2: Traverse folders
            folder_stats = {}
            total_emails = 0

            for folder in sorted(os.listdir(user_path)):
                folder_path = os.path.join(user_path, folder)
                if not os.path.isdir(folder_path):
                    continue

                files = [
                    f
                    for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f))
                ]
                count = len(files)
                folder_stats[folder] = count
                total_emails += count

            # Step 3: Display stats
            table = Table(
                title=f"📊 Email Stats for [cyan]{user}[/cyan]",
                title_style="bold green",
                show_header=True,
                header_style="bold white on dark_magenta",
                box=box.ROUNDED,
                pad_edge=False,
                expand=False,
                row_styles=["none", "dim"],
            )

            table.add_column("📂 Folder", style="cyan", no_wrap=True)
            table.add_column("📨 Emails", justify="right", style="white")

            for folder, count in folder_stats.items():
                table.add_row(folder, str(count))

            self.console.print(table)

            summary_text = Text(
                f"📁 Total Folders: {len(folder_stats)}\n"
                f"✉️ Total Emails: {total_emails}",
                style="bold green",
            )

            self.console.print(
                Panel(
                    summary_text,
                    title="📦 Summary",
                    border_style="green",
                )
            )

        except subprocess.CalledProcessError:
            # This happens if user cancels fzf selection
            pass
        except Exception as e:
            self.console.print(
                Panel.fit(
                    Text(f"❌ Error in :user command: {e}", style="bold red"),
                    border_style="red",
                )
            )

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
                    rprompt=HTML("<ansigray>Type :help or :h for options</ansigray>"),
                )

                if user_input.startswith(":"):
                    cmd = user_input[1:].strip().lower()

                    match cmd:
                        case "browse" | "b":
                            email_path = self.browse_emails()
                            if email_path:
                                self.display_email(email_path)

                        case "user" | "u":
                            self.user_stats()

                        case "analyze" | "a":
                            if self.current_email is not None:
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
                        case "response" | "r":
                            # Placeholder for response generation
                            self.console.print(
                                Panel.fit(
                                    Text(
                                        "🚧 Response Generation is a work in progress",
                                        style="bold yellow",
                                    ),
                                    border_style="yellow",
                                )
                            )

                        case "help" | "h":
                            help_text = """
🌟 Enron Email Intelligence Shell Commands 🌟
:browse/b   - Browse and select emails
:user/u     - Select a user and show email stats
:analyze/a  - Analyze the currently selected email
:help/h     - Show this help menu
:quit/q     - Exit the shell
"""
                            self.console.print(
                                Panel(
                                    Text(help_text, style="green"),
                                    title="💡 Help Menu",
                                    border_style="cyan",
                                )
                            )

                        case "quit" | "q":
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
