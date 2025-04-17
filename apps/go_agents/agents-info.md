# 🧠 AI-Driven Agents (Flask-Connected)

| Agent Name         | Description                                                                           |
| ------------------ | ------------------------------------------------------------------------------------- |
| `summarizer-agent` | Finds emails with `summary IS NULL`, sends body to Flask `/api/summarize`, updates DB |
| `classifier-agent` | Classifies emails via `/api/classify`, updates `label` column                         |
| `ner-agent`        | Extracts named entities via `/api/ner`, stores them in `entities` table               |
| `responder-agent`  | Pre-generates smart replies via `/api/respond` and caches them for Tauri              |

---

# 🦾 System/DB Optimization Agents (SQLite-Only)

| Agent Name          | Description                                                             |
| ------------------- | ----------------------------------------------------------------------- |
| `indexing-agent`    | Adds smart indexes on common query columns (`subject`, `user_id`, etc.) |
| `cleanup-agent`     | Deletes empty, broken, or duplicate emails                              |
| `vacuum-agent`      | Runs `VACUUM;` to compact DB and reduce size                            |
| `healthcheck-agent` | Runs `PRAGMA integrity_check`, logs anomalies, foreign key issues       |
| `migration-agent`   | Adds new columns and populates them (e.g. `word_count`, `read_time`)    |
| `analyzer-agent`    | Runs `ANALYZE;` to help the SQLite planner optimize queries             |
| `archiver-agent`    | Moves old emails to a `archived_emails` table (or flag) based on rules  |

---

# 📬 Data Sync & System Agents

| Agent Name        | Description                                                              |
| ----------------- | ------------------------------------------------------------------------ |
| `imap-agent`      | Connects to IMAP inboxes, pulls messages, stores them into `personal.db` |
| `gmail-agent`     | Google OAuth + Gmail sync via API (if you go cloud-level)                |
| `filewatch-agent` | Watches folders or files and ingests them (for external email logs)      |
| `autosave-agent`  | Periodically backs up SQLite files to an external path                   |

---

# ⚙️ Workflow & DevOps Utility Agents

| Agent Name      | Description                                                                |
| --------------- | -------------------------------------------------------------------------- |
| `commit-agent`  | Makes git commits automatically from system actions (e.g., new data added) |
| `metrics-agent` | Logs internal metrics like email count, unread ratio, avg summary length   |
| `test-agent`    | Simulates traffic against Flask to test responses and load                 |

---

# ⭐ Suggested Starter Set (Recommended Loadout)

| Level   | Agents                                                     |
| ------- | ---------------------------------------------------------- |
| 🥇 MVP  | `summarizer-agent`, `vacuum-agent`, `cleanup-agent`        |
| 🥈 Pro  | + `indexing-agent`, `healthcheck-agent`, `responder-agent` |
| 🥇 AI   | + `classifier-agent`, `ner-agent`                          |
| 🧬 Full | + `imap-agent`, `metrics-agent`, `migration-agent`         |
