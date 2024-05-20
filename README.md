# AI Podcast Cards

## Introduction

This repository contains all components required for the AI Podcast website. The summarizer directory includes scripts for generating summaries from podcast transcripts. The flask_app directory includes the code for the corresponding web application.

### Summarizer

Utilizing the OpenAI API, the summarizer generates structured summaries in JSON format of podcast content.

### Flask App

This web application, developed using Flask and Bootstrap, showcases the generated summaries. It is deployed on Google App Engine and leverages Google Cloud Storage for data handling.

## Installation

To set up the project, follow these steps:

1. Clone the repository:

```zsh
git clone https://github.com/noefischerch/podcast_summaries.git
cd podcast_summaries
```

2. Using the summarizer & development (the deployed Flask app has a separate requirements file):

```zsh
pip install -r dev_requirements.txt
```

3. OpenAI API key

```zsh
export OPENAI_API_KEY='your_api_key_here'
```

## Usage & Configuration

### Configuring the Summarizer

Modify summarizer/config.yml with the necessary settings, such as the model type and API settings.

### Running the Flask App

From the flask_app directory, start the application:

```zsh
flask run app
```

## Contributing

To contribute to this project, please fork the repository, make your changes, and submit a pull request.
