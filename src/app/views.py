from flask import Blueprint, render_template, request, abort, current_app, g
from app.utils import list_files, load_summaries, load_summary_by_id, convert_date

main = Blueprint("main", __name__)


@main.before_request
def load_config():
    g.bucket_name = current_app.config["BUCKET_NAME"]
    g.sum_prefix = current_app.config["SUM_PREFIX"]
    g.podcasts = current_app.config["PODCASTS"]


@main.route("/")
def index():
    query = request.args.get("query", "")
    podcast_filter = request.args.get("podcast", "")
    page = int(request.args.get("page", 1))
    per_page = 10

    file_paths = list_files(g.bucket_name, g.sum_prefix)
    all_summaries = load_summaries(g.bucket_name, file_paths)

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

    return render_template(
        "index.html",
        summaries=displayed_summaries,
        podcast_names=g.podcasts,
        total_pages=total_pages,
        current_page=page,
        query=query,
        podcast_filter=podcast_filter,
    )


@main.route("/summary/<summary_id>")
def summary(summary_id):
    summary = load_summary_by_id(
        g.bucket_name,
        g.sum_prefix,
        summary_id,
    )
    summary["metadata"]["date"] = convert_date(summary["metadata"]["date"])

    if summary is None:
        abort(404, description="Summary not found")
    return render_template("summary.html", data=summary)
