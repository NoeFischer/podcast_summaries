import pytest
from unittest.mock import patch


@pytest.fixture
def summary_data():
    return {
        "metadata": {
            "title": "Ilya Sutskever (OpenAI Chief Scientist) - Building AGI, Alignment, Future Models, Spies, Microsoft, Taiwan, & Enlightenment",
            "date": "27-03-2023",
            "participants": ["Ilya Sutskever", "Dwarkesh Patel"],
            "id": "dwarkesh_podcast_230327",
            "podcast": "Dwarkesh Podcast",
        },
        "summary": "In this episode, Ilya Sutskever, Co-founder and Chief Scientist at OpenAI, engages in a comprehensive discussion on various facets of AI development. Key topics include the timeline for achieving Artificial General Intelligence (AGI), the evolution beyond current generative models, the intricacies of AI alignment with human values, and the envisaged future post-AGI. The dialogue also touches upon the collaboration with Microsoft and addresses the challenges posed by potential leaks and espionage in AI research.",
        "topics": [
            "Time to AGI",
            "Alignment",
            "Post AGI Future",
            "Generative models",
            "Collaboration with Microsoft",
        ],
        "quotes": [
            {
                "quote": "It's hard to answer that question. I try really hard, I give it everything I've got and that has worked so far. I think that's all there is to it.",
                "speaker": "Ilya Sutskever",
            },
            {
                "quote": "Maybe they haven't really gotten to do it a lot. But it also wouldn't surprise me if some of it was going on right now.",
                "speaker": "Ilya Sutskever",
            },
            {
                "quote": "If your base neural net is smart enough, you just ask it — What would a person with great insight, wisdom, and capability do?",
                "speaker": "Ilya Sutskever",
            },
        ],
        "terms": {
            "AGI": "Artificial General Intelligence, the hypothetical ability of an AI system to understand or learn any intellectual task that a human being can.",
            "Alignment": "Ensuring that AI systems' goals are aligned with human values and objectives to prevent unintended consequences.",
            "Generative Models": "Models that learn to generate new data samples from the same distribution as the training data.",
            "Post AGI Future": "The hypothetical future state of society after the development of Artificial General Intelligence.",
        },
        "recommendations": [
            "Alignment research is a crucial area for academic researchers to contribute meaningfully.",
            "Understanding and improving reliability and controllability of AI models are key for future progress.",
            "Continued research and progress in developing larger and more efficient models are essential for the AI ecosystem.",
            "Strengthen security measures to prevent leaks and espionage within AI research.",
            "Enhance collaboration with industry leaders like Microsoft to leverage their resources and expertise.",
        ],
        "conclusions": "The discussion with Ilya Sutskever sheds light on critical aspects of AI development, including the challenges of achieving AGI, the importance of alignment, and the potential impact of AI on society. It emphasizes the need for ongoing research and innovation to address complex issues in the field.",
    }


@patch("app.views.load_summaries")
@patch("app.views.list_files")
def test_index(mock_list_files, mock_load_summaries, client, summary_data):
    mock_list_files.return_value = ["summaries/summary1.json"]
    mock_load_summaries.return_value = [summary_data]
    response = client.get("/?query=Ilya Sutskever")
    assert response.status_code == 200
    assert b"Ilya Sutskever" in response.data


@patch("app.views.load_summaries")
@patch("app.views.list_files")
def test_index_pagination(mock_list_files, mock_load_summaries, client, summary_data):
    mock_list_files.return_value = ["summaries/summary1.json"] * 20
    mock_load_summaries.return_value = [summary_data.copy() for _ in range(20)]
    response = client.get("/?page=2")
    assert response.status_code == 200
    assert b"Ilya Sutskever" in response.data


@patch("app.views.load_summary_by_id")
def test_summary_valid_id(mock_load_summary_by_id, client, summary_data):
    mock_load_summary_by_id.return_value = summary_data
    response = client.get("/summary/dwarkesh_podcast_230327")
    assert response.status_code == 200
    assert b"Ilya Sutskever" in response.data


@patch("app.views.load_summary_by_id")
def test_summary_invalid_id(mock_load_summary_by_id, client, summary_data):
    mock_load_summary_by_id.return_value = None
    response = client.get("/summary/invalid_id")
    assert response.status_code == 404
    assert "Summary not found" in response.get_data(as_text=True)
