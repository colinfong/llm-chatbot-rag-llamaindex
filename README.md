# Wikipedia RAG Chatbot

A browser-based chatbot that answers questions using Wikipedia pages you choose. You tell it
which pages to read, and it answers from those pages instead of relying only on what the AI
model already knows.

This technique is called **RAG** (Retrieval-Augmented Generation): the app first *retrieves*
relevant text, then the model *generates* an answer from it.

## How it works

1. **You pick the pages.** In the settings panel, type something like
   `please index: Paris, Lagos`.
2. **It finds the page names in your request.** An OpenAI model reads what you typed and
   returns a clean list, such as `["Paris", "Lagos"]`.
3. **It downloads the pages** from Wikipedia.
4. **It splits the text into chunks** of about 150 tokens, with a small overlap so ideas aren't
   cut off at chunk boundaries.
5. **It turns each chunk into a vector** (an embedding), a list of numbers that captures its
   meaning. The vectors go into an in-memory vector store that can find chunks by meaning
   rather than exact words.
6. **A ReAct agent answers your questions.** It decides whether it needs to search the index,
   retrieves the 10 most relevant chunks, and writes an answer from them.

The index lives in memory only, so pages are downloaded and indexed again whenever the app
restarts or the settings change.

## Built with

| Tool | Role |
|---|---|
| [Python](https://www.python.org/) 3.12 | Language. Newer versions crash Chainlit on startup (see [Troubleshooting](#troubleshooting)). |
| [LlamaIndex](https://www.llamaindex.ai/) 0.12.52 | RAG framework: Wikipedia loading, chunking, vector index, query engine, ReAct agent. |
| [OpenAI API](https://platform.openai.com/) (`gpt-4o-mini`) | Reads page requests, drives the agent's reasoning, writes answers, and creates embeddings. |
| [Chainlit](https://chainlit.io/) 2.11.0 | Chat UI: browser interface, settings panel, and message handling. |
| [Pydantic](https://docs.pydantic.dev/) | Defines the page-list structure so the model returns structured data. |
| [wikipedia](https://pypi.org/project/wikipedia/) | Fetches page content for LlamaIndex's `WikipediaReader`. |
| [PyYAML](https://pyyaml.org/) | Reads the OpenAI API key from `apikeys.yml`. |

## Project structure

| File | Purpose |
|---|---|
| `index_wikipages.py` | Turns a page request into a searchable vector index (steps 2–5). Run it directly to test indexing. |
| `chat_agent.py` | The Chainlit app: settings panel, agent setup, and chat replies. |
| `utils.py` | Loads the OpenAI API key. |
| `requirements.txt` | Pinned package versions. |

## Setup

You'll need Python 3.12 and an [OpenAI API key](https://platform.openai.com/api-keys).

1. Create a virtual environment and install the dependencies:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create `apikeys.yml` in the project root with your key:
   ```yaml
   openai:
     api_key: <your OpenAI key>
   ```
   This file is listed in `.gitignore`. Never commit it.

## Usage

1. Start the app:
   ```bash
   chainlit run chat_agent.py
   ```
   It opens at http://localhost:8000. Add `-w` to reload automatically when you save a file.
2. Open the **settings** panel (the gear icon next to the chat input).
3. In **Request Wikipage(s)**, enter something like `please index: Paris, Lagos` and confirm.
4. Wait for "Wikipage(s) ... successfully indexed", then ask a question about those pages.

## Troubleshooting

- **Blank page, with `NoEventLoopError` or "Timeout should be used inside a task" in the
  terminal:** your venv uses Python 3.13 or newer. Chainlit calls `nest_asyncio`, which breaks
  on newer Python. Rebuild the venv with Python 3.12.
- **"Agent is not available":** you haven't indexed any pages yet. Use the settings panel first.
- **Wrong page indexed:** page names must match Wikipedia titles. Auto-suggest is turned off
  because it "corrects" names (for example, `paris` to `parks`).
