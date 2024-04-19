import json
import os
import re

import streamlit as st


def load_css(file_name):
    with open(file_name) as f:
        css_content = f"<style>{f.read()}</style>"
    st.markdown(css_content, unsafe_allow_html=True)


def load_data(directory, selected_podcast):
    summary_files = [f for f in os.listdir(directory) if f.endswith(".json")]
    summaries = {}
    for file_name in summary_files:
        podcast_name = format_podcast_name(file_name)
        if podcast_name == selected_podcast:
            with open(f"{directory}/{file_name}", "r") as file:
                data = json.load(file)
            summaries[data["metadata"]["title"]] = data
    return summaries


def format_podcast_name(file_name):
    match = re.match(r"(.+)_\d{6}.json$", file_name)
    if match:
        return " ".join(word.capitalize() for word in match.group(1).split("_"))
    return None


def create_html(content, content_type):
    if content_type == "tags":
        return "".join(f'<span class="tag">{tag}</span>' for tag in content)
    elif content_type == "quote":
        quote, speaker = content
        return f'<div class="quote-container">"{quote}"<span class="quote-author"> {speaker}</span></div>'
    elif content_type == "recommendations":
        return (
            '<ul class="recommendation-list">'
            + "".join(f"<li>{rec}</li>" for rec in content)
            + "</ul>"
        )
    elif content_type == "glossary":
        term, definition = content
        search_query = "+".join(term.split())
        return f'<div class="glossary-term"><a href="https://perplexity.ai/search?q={search_query}" target="_blank" rel="noopener noreferrer" class="term-title" style="color: #2c3e50; text-decoration: none;">{term}</a><div class="term-definition">{definition}</div></div>'


def display_podcast_info(data):
    header = (
        f'<h2 class="custom-subheader">{data["metadata"]["date"]} | '
        + " • ".join(data["metadata"]["participants"])
        + "</h2>"
    )
    st.markdown(header, unsafe_allow_html=True)


@st.cache_data()
def get_podcast_names(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    return sorted(set(format_podcast_name(f) for f in files if format_podcast_name(f)))


def main():
    load_css("style.css")

    st.markdown(
        '<h1 class="custom-header">AI Podcast Summaries</h1>', unsafe_allow_html=True
    )

    directory = "../data/summaries/"
    podcast_names = get_podcast_names(directory)

    selected_podcast = st.session_state.get(
        "selected_podcast", podcast_names[0] if podcast_names else None
    )
    for podcast in podcast_names:
        if st.button(podcast):
            selected_podcast = podcast
            st.session_state["selected_podcast"] = podcast

    summaries = load_data(directory, selected_podcast)
    selected_title = st.selectbox("Select an Episode", list(summaries.keys()))

    data = summaries[selected_title]
    display_podcast_info(data)
    st.markdown('<h3 class="custom-subheader">Summary</h3>', unsafe_allow_html=True)
    st.write(data["summary"])

    st.markdown('<h3 class="custom-subheader">Quotes</h3>', unsafe_allow_html=True)
    for quote in data["quotes"]:
        st.markdown(
            create_html((quote["quote"], quote["speaker"]), "quote"),
            unsafe_allow_html=True,
        )

    st.markdown(
        '<h3 class="custom-subheader">Recommendations</h3>', unsafe_allow_html=True
    )
    st.markdown(
        create_html(data["recommendations"], "recommendations"), unsafe_allow_html=True
    )

    st.markdown('<h3 class="custom-subheader">Conclusions</h3>', unsafe_allow_html=True)
    st.write(data["conclusions"])

    st.markdown('<h3 class="custom-subheader">Glossary</h3>', unsafe_allow_html=True)
    for term, definition in data["terms"].items():
        st.markdown(create_html((term, definition), "glossary"), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
