# LLM Chatbot with RAG (LlamaIndex + Chainlit)

Learning project: a Chainlit chat UI where the user names Wikipedia pages, they get indexed
into an in-memory vector store, and a ReAct agent answers questions using that index as a tool.
Files came from a course template with `# REPLACE THIS WITH YOUR CODE` placeholders that
the user fills in themselves.

## Files
- `index_wikipages.py` — `create_index(query)`: an LLM (OpenAIPydanticProgram) extracts page
  names after "please index:", WikipediaReader loads them, SentenceSplitter (150/45) chunks
  them, VectorStoreIndex builds the index. Run directly to test indexing.
- `chat_agent.py` — Chainlit app. Chat settings (model select + wiki page text input) trigger
  `setup_agent`, which builds the index and a ReActAgent with a "Wikipedia" QueryEngineTool.
- `utils.py` — `get_apikey()` reads the OpenAI key from `apikeys.yml`.

## Running
- Use the project venv: `source .venv/bin/activate`. It must be Python 3.12: chainlit calls
  `nest_asyncio.apply()` on startup, which breaks async on newer Python (3.15 crashed with
  `NoEventLoopError` / "Timeout should be used inside a task", leaving a blank page).
- Rebuild: `/opt/homebrew/bin/python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- App: `chainlit run chat_agent.py`
- Indexing only: `python index_wikipages.py`

## Gotchas
- `apikeys.yml` holds the OpenAI key and is gitignored. Never print, log, or commit it.
- Pinned versions: llama-index 0.12.52, chainlit 2.11.0. Use `gpt-4o-mini`: the default
  gpt-3.5-turbo is deprecated and this llama-index doesn't support gpt-5 models.
- Chainlit 2.x imports from `chainlit.input_widget` (older versions: `input_widgets`).
- WikipediaReader needs `auto_suggest=False` ("paris" otherwise becomes "parks") and a custom
  user agent to avoid rate limits.

## Working with the user
- They're learning: explain changes briefly and keep code close to the template's style.
  Don't fill placeholders unless asked.

## Status (update at end of each session)
- Done: `index_wikipages.py` (committed 2026-10-30, "Implement Wikipedia page indexing").
- Done, uncommitted: all of `chat_agent.py` through Task 11. The agent is stored per user in
  `cl.user_session` ("agent"); `main` reads it and sends `response.response`.
- 2026-11-03: rebuilt `.venv` on Python 3.12 (old one kept as `.venv-py315`, safe to delete).
  Server starts and serves the page.
- Next: test indexing and a chat question in the browser, then commit.
