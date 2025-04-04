import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import toml

# Reconstructed task assignments from previous conversation
with open("issues-github.toml", "r") as f:
    data = toml.load(f)

# Flatten tasks from all phases
tasks = []
for phase, content in data.items():
    if phase.startswith("phase"):
        for task in content["tasks"]:
            tasks.append(
                {
                    "Task": task["name"],
                    "Start": datetime.strptime(task["start_date"], "%Y-%m-%d"),
                    "End": datetime.strptime(task["end_date"], "%Y-%m-%d"),
                    "Assignee": task["assignee"],
                }
            )
# Create DataFrame
df = pd.DataFrame(tasks, columns=["Task", "Start", "End", "Assignee"])
df["Start"] = pd.to_datetime(df["Start"])
df["End"] = pd.to_datetime(df["End"])

# Sort by start date
df = df.sort_values("Start")

# Plot
fig, ax = plt.subplots(figsize=(15, 14))
colors = plt.cm.tab20.colors

# Plot horizontal bars
for i, row in df.iterrows():
    ax.barh(
        y=row["Task"],
        width=(row["End"] - row["Start"]).days,
        left=row["Start"],
        color=colors[hash(row["Assignee"]) % len(colors)],
        label=row["Assignee"],
    )

# Format x-axis
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
plt.xticks(rotation=45)

# Set labels
ax.set_xlabel("Date")
ax.set_title("📅 Project Gantt Chart – Enron Email System")

# Deduplicate legend
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(
    by_label.values(),
    by_label.keys(),
    title="Assignee",
    bbox_to_anchor=(1.05, 1),
    loc="upper left",
)

plt.tight_layout()
plt.grid(True)
plt.show()
