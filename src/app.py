import json

import streamlit as st


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def create_tags_html(tags):
    tags_html = ""
    for tag in tags:
        tags_html += f'<span class="tag">{tag}</span>'
    return tags_html


def create_quote_html(quote, speaker):
    return f"""
    <div class="quote-container">
        "{quote}"
        <span class="quote-author"> {speaker}</span>
    </div>
    """


def create_recommendations_html(recommendations):
    recommendations_html = '<ul class="recommendation-list">'
    for recommendation in recommendations:
        recommendations_html += f"<li>{recommendation}</li>"
    recommendations_html += "</ul>"
    return recommendations_html


def create_glossary_html(term, definition):
    search_query = "+".join(term.split())
    return f"""
    <div class="glossary-term">
        <a href="https://perplexity.ai/search?q={search_query}" target="_blank" rel="noopener noreferrer" class="term-title" style="color: #2c3e50; text-decoration: none;">{term}</a>
        <div class="term-definition">{definition}</div>
    </div>
    """


# Load external CSS
load_css("style.css")

# Load JSON data from file
with open("../data/summaries/final_summary.json", "r") as file:
    data = json.load(file)

st.markdown(
    f'<h1 class="custom-header">{data["metadata"]["title"]}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<h2 class="custom-subheader">{data["metadata"]["date"]} | '
    + " • ".join(data["metadata"]["participants"])
    + "</h2>",
    unsafe_allow_html=True,
)

# Topics
st.markdown(create_tags_html(data["topics"]), unsafe_allow_html=True)

# Summary
st.markdown('<h3 class="custom-subheader">Summary</h3>', unsafe_allow_html=True)
st.write(data["summary"])

# Quotes
st.markdown('<h3 class="custom-subheader">Quotes</h3>', unsafe_allow_html=True)
for quote in data["quotes"]:
    quote_html = create_quote_html(quote["quote"], quote["speaker"])
    st.markdown(quote_html, unsafe_allow_html=True)

# Recommendations
st.markdown('<h3 class="custom-subheader">Recommendations</h3>', unsafe_allow_html=True)
recommendations_html = create_recommendations_html(data["recommendations"])
st.markdown(recommendations_html, unsafe_allow_html=True)

# Conclusions
st.markdown('<h3 class="custom-subheader">Conclusions</h3>', unsafe_allow_html=True)
st.write(data["conclusions"])

# Glossary
st.markdown('<h3 class="custom-subheader">Glossary</h3>', unsafe_allow_html=True)
for term, definition in data["terms"].items():
    glossary_html = create_glossary_html(term, definition)
    st.markdown(glossary_html, unsafe_allow_html=True)
