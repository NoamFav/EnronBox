import os
import subprocess
import email
from typing import Optional, Dict, Any

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

# Import the classifier
from app.services.enron_classifier import EnronEmailClassifier
from app.services.responder import EmailResponder
from app.services.summarizer import EmailSummarizer

from app.services.ner_engine import Extractor
from app.services.db import update_email_flags, get_email_flags


class EnronMailShell:
    def __init__(self, maildir_path: str, max_emails: int = 5000):
        # Ensure the path exists and is absolute
        self.maildir_path = os.path.abspath(maildir_path)

        # Validate maildir path
        if not os.path.exists(self.maildir_path):
            raise FileNotFoundError(f"Maildir path not found: {self.maildir_path}")

        self.current_email: Optional[Dict[str, Any]] = None
        self.classifier = EnronEmailClassifier()
        self.responder = EmailResponder(self.classifier)
        self.summarizer = EmailSummarizer()
        self.console = Console()

        self.extrator = Extractor()

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
                enron_db_path=self.maildir_path, max_emails=max_emails
            )
            self.classifier.train(email_df, labels)
            self.console.print(
                Panel.fit(
                    Text("✅ Email Classifier Loaded Successfully", style="bold green"),
                    border_style="green",
                )
            )
        except (FileNotFoundError, ValueError) as e:
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

    def summarize_current_email(self):
        """
        Generate a summary of the currently selected email
        """
        if self.current_email is None:
            self.console.print(
                Panel.fit(
                    Text("❌ No email selected. Use :browse first.", style="red"),
                    border_style="red",
                )
            )
            return

        # Reconstruct full email text
        full_email_text = f"""
Subject: {self.current_email.get('subject', '')}
From: {self.current_email.get('sender', '')}
Body: {self.current_email.get('body', '')}
        """

        # Generate summary
        try:
            summary = self.summarizer.summarize_email(full_email_text)

            # Display summary
            self.console.print(
                Panel(
                    Text(summary, style="cyan"),
                    title="📝 Email Summary",
                    border_style="green",
                )
            )
        except (ValueError, TypeError, AttributeError) as e:
            self.console.print(
                Panel.fit(
                    Text(f"❌ Error generating summary: {e}", style="red"),
                    border_style="red",
                )
            )

    def _fzf_select(self, options: list[str]) -> Optional[str]:
        """Use fzf to select from a list of options"""
        try:
            proc = subprocess.Popen(
                ["fzf", "--height", "50%", "--layout=reverse", "--border"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            input_data = "\n".join(options)
            stdout, _ = proc.communicate(input=input_data)
            return stdout.strip()
        except (OSError, ValueError, subprocess.CalledProcessError) as e:
            self.console.print(f"[bold red]fzf error: {e}[/bold red]")
            return None

    def browse_emails(self) -> Optional[str]:
        """Browse and select emails using fzf (cross-platform safe)"""
        try:
            # Select user
            users = sorted(os.listdir(self.maildir_path))
            user = self._fzf_select(users)
            if not user:
                return None

            # Select folder
            folders = sorted(os.listdir(os.path.join(self.maildir_path, user)))
            folder = self._fzf_select(folders)
            if not folder:
                return None

            # Select email
            folder_path = os.path.join(self.maildir_path, user, folder)
            files = sorted(f for f in os.listdir(folder_path) if not f.startswith("."))
            email_file = self._fzf_select(files)
            if not email_file:
                return None

            # Return full path
            full_path = os.path.join(folder_path, email_file)
            return full_path

        except (FileNotFoundError, OSError) as e:
            self.console.print(f"[bold red]Error accessing file system: {e}[/bold red]")
            return None
        except ValueError as e:
            self.console.print(f"[bold red]Value error: {e}[/bold red]")
            return None

    def generate_response(self, email_data: Dict[str, Any]) -> str:
        """Generate a response to the email"""
        response = self.responder.generate_reply(email_data)
        return response

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

            # Generate Email Summary
            full_email_text = f"""
    Subject: {subject}
    From: {sender}
    Body: {body}
            """
            summary = self.summarizer.summarize_email(full_email_text)

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
                f"{prediction['category']}"
                "(Confidence: {prediction['confidence']:.2%})",
            )
            emotions_text = (
                f"Polarity: {prediction['emotion']['polarity']:.2f}, "
                f"Subjectivity: {prediction['emotion']['subjectivity']:.2f}, "
                f"Stress: {prediction['emotion']['stress_score']:.2f}, "
                f"Relaxation: {prediction['emotion']['relaxation_score']:.2f}"
            )

            table.add_row("🎭 Emotional Tone", emotions_text)

            entities = self.extrator.extract_entities(email_data["body"])
            entities_str = (
                f"Names: {entities['names']}\nOrgs:"
                "{entities['orgs']}\nDates: {entities['dates']}"
            )
            table.add_row("🏷️ Entities", entities_str)

            # Add summary row
            table.add_row("📋 Summary", summary)

            # Body preview
            body_panel = Panel(
                Syntax(body, "txt", theme="monokai", line_numbers=False),
                title="Body Preview",
                border_style="green",
            )

            response = self.generate_response(email_data)

            self.console.print(table)
            self.console.print(body_panel)
            self.console.print(
                Panel(
                    Text(response, style="cyan"),
                    title="📧 AI Response (Not AI but soon!)",
                    border_style="green",
                )
            )

            self.current_email = email_data
            return email_data

        except (FileNotFoundError, OSError, email.errors.MessageParseError) as e:
            # Handle specific exceptions related to file reading and email parsing
            self.console.print(f"[bold red]Error reading email: {e}[/bold red]")
            return None
        except (KeyError, ValueError) as e:
            # Handle specific exceptions for missing keys or invalid values
            self.console.print(f"[bold red]Error processing email data: {e}", style="red")
            return None

    def user_stats(self):
        """Display email statistics for a selected user"""
        try:
            # Pick user safely
            users = sorted(os.listdir(self.maildir_path))
            user = self._fzf_select(users)
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

            # Traverse folders
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

            # Display stats
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

        except FileNotFoundError as e:
            # Handle file or folder not found
            self.console.print(
                Panel.fit(
                    Text(f"❌ File or folder not found: {e}", style="bold red"),
                    border_style="red",
                )
            )

        except OSError as e:
            # Handle OS-related errors (e.g., permissions issues)
            self.console.print(
                Panel.fit(
                    Text(f"❌ OS error: {e}", style="bold red"),
                    border_style="red",
                )
            )

        except subprocess.CalledProcessError as e:
            # Handle subprocess-related errors
            self.console.print(
                Panel.fit(
                    Text(f"❌ Subprocess error: {e}", style="bold red"),
                    border_style="red",
                )
            )

        except ValueError as e:
            # Handle invalid values (e.g., if a value isn't what you expect)
            self.console.print(
                Panel.fit(
                    Text(f"❌ Value error: {e}", style="bold red"),
                    border_style="red",
                )
            )

    def named_entity_recognition(self):
        """Extract named entities from email"""
        if self.current_email is not None:
            email_body = self.current_email["body"]
            entities = self.extrator.extract_entities(email_body)
            extracted_entities = f"""
        👤 Names:  {entities['names']}
        🏢 Orgs:   {entities['orgs']}
        📅 Dates:  {entities['dates']}
        """

            self.console.print(
                Panel(
                    Text(extracted_entities, style="cyan"),
                    title="🏷️ Entity Extraction Results",
                    border_style="green",
                )
            )
        else:
            self.console.print(
                Panel.fit(
                    Text("❌ No email selected. Use :browse first.", style="red"),
                    border_style="red",
                )
            )

    def sync_email_flags(
        self,
        email_id: int,
        read=None,
        starred=None,
        important=None,
        deleted=None,
    ):
        """
        Sync email flags to the database.
        """
        update_email_flags(
            email_id, read=read, starred=starred, important=important, deleted=deleted
        )

    def fetch_email_flags(self, email_id: int):
        """
        Fetch email flags from the database.
        """
        return get_email_flags(email_id)

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
      - Stress Score:  {prediction['emotion']['stress_score']:.2f}
      - Relaxation Score:  {prediction['emotion']['relaxation_score']:.2f}
    """
                                self.console.print(
                                    Panel(
                                        Text(detailed_analysis, style="cyan"),
                                        title="📊 AI Insights",
                                        border_style="green",
                                    )
                                )
                        case "response" | "r":
                            if self.current_email is not None:
                                response = self.responder.generate_reply(
                                    self.current_email
                                )
                                self.console.print(
                                    Panel(
                                        Text(response, style="cyan"),
                                        title="✉️ Generated Response",
                                        border_style="green",
                                    )
                                )
                            else:
                                self.console.print(
                                    Panel.fit(
                                        Text(
                                            "❌ No email selected. Use :browse first.",
                                            style="red",
                                        ),
                                        border_style="red",
                                    )
                                )
                        case "summary" | "s":
                            self.summarize_current_email()

                        case "entities" | "e":
                            self.named_entity_recognition()

                        case "help" | "h":
                            help_text = """
🌟 Enron Email Intelligence Shell Commands 🌟
:browse/b   - Browse and select emails
:user/u     - Select a user and show email stats
:analyze/a  - Analyze the currently selected email
:response/r - Generate a response to the selected email
:summary/s  - Generate a summary of the selected email
:entities/e - Extract named entities from the currently selected email
:help/h     - Show this help menu
:clear/c    - Clear the screen
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

                        case "clear" | "c":
                            os.system("cls" if os.name == "nt" else "clear")

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
