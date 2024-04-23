import json
from datetime import datetime

from flask import Flask, render_template, request
from utils import list_files

app = Flask(__name__)

SUMMARIES_DIR = "../../data/summaries"

# Get all summaries
summaries = []
for file_name in list_files(SUMMARIES_DIR, "json"):
    with open(file_name, "r") as file:
        summary = json.load(file)
        summary["metadata"]["date"] = datetime.strptime(
            summary["metadata"]["date"], "%d-%m-%Y"
        ).strftime("%Y-%m-%d")
        summaries.append(summary)

# sort summaries
summaries.sort(key=lambda x: x["metadata"]["date"], reverse=True)

# Get unique podcast names
podcast_names = set(summary["metadata"]["podcast"] for summary in summaries)


@app.route("/")
def index():
    # search filter
    query = request.args.get("query")
    if query:
        filtered_summaries = [
            summary
            for summary in summaries
            if query.lower() in summary["metadata"]["title"].lower()
        ]
    else:
        filtered_summaries = summaries

    # podcast filter
    podcast_filter = request.args.get("podcast")
    if podcast_filter:
        filtered_summaries = [
            summary
            for summary in filtered_summaries
            if summary["metadata"]["podcast"] == podcast_filter
        ]

    return render_template(
        "index.html", summaries=filtered_summaries, podcast_names=podcast_names
    )


@app.route("/summary/<int:summary_id>")
def summary(summary_id):
    data = next(
        (summary for summary in summaries if summary["metadata"]["id"] == summary_id),
        None,
    )
    if data is None:
        return "Post not found", 404
    return render_template("summary.html", data=data)


if __name__ == "__main__":
    app.run()
