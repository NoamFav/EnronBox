from app.ui.enron_shell import EnronMailShell
from app.routes.emails import emails_bp
from flask import request, jsonify, Flask
from flask_cors import CORS
from app.services import db
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


app = Flask(__name__)
CORS(app)
app.register_blueprint(emails_bp, url_prefix="/api")

def main():
    maildir_path = "./maildir"
    max_emails = 5000

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
            "Please download the Enron dataset by running:"
            "'./scripts/download_enron.sh' "
            "or for Windows, 'download_enron.cmd'"
        )
        sys.exit(1)

    shell = EnronMailShell(maildir_path, max_emails)
    shell.run()

@app.route('/api/emails/<email_id>/status', methods=['POST', 'OPTIONS'])
def update_email_status(email_id):

    if request.method == 'OPTIONS':
         return '', 200
    
    status_update = request.json
    print(f"Received status update for email {email_id}:", status_update)
    
    success = db.store_email_status(email_id, status_update)
    if success:
        return jsonify({"message": "Email status updated successfully"}), 200
    return jsonify({"message": "Failed to update email status"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
