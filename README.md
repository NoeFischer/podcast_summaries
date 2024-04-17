# Podcast Summarization

## Process
0. Get transcripts
1. Split podcast transcripts into equal-sized chunks (max 16K tokens)
    - .txt files
2. Create intermediate summaries of each of the podcast chunks:
    - response_format: json_object
    - user prompt: provide structure to align the json structure of the different chunks/transcripts
    - save summaries as json files
    - skip api call if intermediate summary already exists
3. Combine summaries
    - Combine the json files into one json file
    - "summary" : [summary1, summary2, ...], ...
4. Summarize the summaries
    - Transform summaries to text that the LLM can understand. 
    - Is it possible to pass json?
    - save final summary as json
    - skip if intermediate summary already exists
5. Streamlit app

## TODOs
- Build a scraper:
    - metadata
    - transcripts
- How to store the data? 
- Is it possible to do it with one user prompt for both stages?
- Can you pass json to the openai api?
