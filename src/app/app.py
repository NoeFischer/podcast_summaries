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

BUCKET_NAME = config.get("bucket_name")
SUMMARIES_PREFIX = config.get("summaries_prefix")
PODCASTS = config.get("podcasts")


app = Flask(__name__)


@app.route("/")
def index():
    query = request.args.get("query", "")
    podcast_filter = request.args.get("podcast", "")
    page = int(request.args.get("page", 1))
    per_page = 10

    file_paths = list_files(BUCKET_NAME, SUMMARIES_PREFIX)
    all_summaries = load_summaries(BUCKET_NAME, file_paths)

    filtered_summaries = [
        summary
        for summary in all_summaries
        if (not query or query.lower() in summary["metadata"]["title"].lower())
        and (not podcast_filter or summary["metadata"]["podcast"] == podcast_filter)
    ]

    for summary in filtered_summaries:
        summary["metadata"]["date"] = convert_date(summary["metadata"]["date"])

    filtered_summaries.sort(key=lambda x: x["metadata"]["date"], reverse=True)

    total_summaries = len(filtered_summaries)
    total_pages = (total_summaries + per_page - 1) // per_page
    displayed_summaries = filtered_summaries[(page - 1) * per_page : page * per_page]

    podcast_names = PODCASTS
    return render_template(
        "index.html",
        summaries=displayed_summaries,
        podcast_names=podcast_names,
        total_pages=total_pages,
        current_page=page,
        query=query,
        podcast_filter=podcast_filter,
    )


@app.route("/summary/<summary_id>")
def summary(summary_id):
    summary = load_summary_by_id(BUCKET_NAME, SUMMARIES_PREFIX, summary_id)
    summary["metadata"]["date"] = convert_date(summary["metadata"]["date"])

    if summary is None:
        abort(404, description="Summary not found")
    return render_template("summary.html", data=summary)


if __name__ == "__main__":
    app.run()
