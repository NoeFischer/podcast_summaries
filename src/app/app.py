# TODO: only show like 10 summaries at a time, and have a "load more" button, but the search should still work

from flask import Flask, abort, render_template, request

from app.utils import (
    list_files,
    load_summaries,
    load_summary_by_id,
    load_config,
    convert_date,
)

config = load_config("config.yml")

SUMMARIES_DIR = config.get("SUMMARIES_DIR")
PODCASTS = config.get("PODCASTS")

app = Flask(__name__)


@app.route("/")
def index() -> str:
    query = request.args.get("query")
    podcast_filter = request.args.get("podcast")

    summaries = load_summaries(list_files(SUMMARIES_DIR), query, podcast_filter)

    for summary in summaries:
        summary["metadata"]["date"] = convert_date(summary["metadata"]["date"])

    summaries.sort(key=lambda x: x["metadata"]["date"], reverse=True)

    podcast_names = PODCASTS
    return render_template(
        "index.html", summaries=summaries, podcast_names=podcast_names
    )


@app.route("/summary/<summary_id>")
def summary(summary_id):
    summary = load_summary_by_id(SUMMARIES_DIR, summary_id)
    summary["metadata"]["date"] = convert_date(summary["metadata"]["date"])

    if summary is None:
        abort(404, description="Summary not found")
    return render_template("summary.html", data=summary)


if __name__ == "__main__":
    app.run()
