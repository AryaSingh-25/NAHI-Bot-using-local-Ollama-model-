# NAHI-Bot-using-local-Ollama-model-
```md
A fully local AI-powered assistant built with Streamlit and Ollama to answer questions about the National Highways Authority of India (NHAI) using a custom text-based knowledge base.

This application runs entirely on your local machine with no external APIs, ensuring complete privacy and unlimited usage.

## Features

- Fully local and private (no cloud APIs)
- Powered by Ollama (LLaMA, Gemma, etc.)
- Knowledge-base driven responses
- Maintains chat context
- Professional Streamlit UI
- No API limits or rate restrictions

## Tech Stack

- Python
- Streamlit
- Ollama
- Local Large Language Models (LLaMA 3, Gemma, etc.)

## Project Structure

```
```txt
.
├── app.py
├── data/
│   ├── topic1.txt
│   ├── topic2.txt
│   └── ...
├── requirements.txt
└── README.md
```

````

Each `.txt` file inside the `data` folder represents one knowledge topic.  
Files must contain more than 100 characters to be loaded.

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install streamlit requests
````

### 2. Install and Run Ollama

Download Ollama from:
[https://ollama.ai](https://ollama.ai)

Start the Ollama server:

```bash
ollama serve
```

Pull a model (example):

```bash
ollama pull llama3
```

### 3. Prepare Knowledge Base

Create a `data` directory and add `.txt` files related to NHAI topics:

```txt
data/
├── nhai_overview.txt
├── bharatmala_pariyojana.txt
├── fastag.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser.

## Usage

* Select an available Ollama model from the sidebar
* Ask questions related to NHAI policies, projects, or initiatives
* The assistant answers using the loaded knowledge base and chat context

## Example Questions

* What does NHAI stand for?
* What is Bharatmala Pariyojana?
* Explain the Green Highways Policy
* What is FASTag?
* What road safety initiatives does NHAI run?

## How It Works

1. Loads all valid `.txt` files from the data directory
2. Ranks topics based on relevance to the user query
3. Builds a contextual prompt from top matching topics
4. Sends the prompt to Ollama’s local API
5. Displays a concise, professional response

## Privacy

* Runs completely offline
* No data is sent to external servers
* Suitable for internal, academic, or government use

## Version

NHAI AI Assistant v3.0
Built with Streamlit and Ollama

```txt

## Data Usage Notice

This project uses locally generated knowledge files created from publicly available
information related to the National Highways Authority of India (NHAI).

To avoid potential licensing or redistribution issues, the knowledge files are not
included in this repository.

Users are expected to generate their own local knowledge base or manually add
summarized content to the `data/` directory.

```

