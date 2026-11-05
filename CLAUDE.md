# LLM Chatbot with RAG (LlamaIndex + Chainlit)

A Chainlit chat UI where the user names Wikipedia pages, they get indexed into an in-memory
vector store, and a ReAct agent answers questions using that index as a tool.

## Files
- `index_wikipages.py` — `create_index(query)`: an LLM (OpenAIPydanticProgram) extracts page
  names after "please index:", WikipediaReader loads them, SentenceSplitter (150/45) chunks
  them, VectorStoreIndex builds the index. Run directly to test indexing.
- `chat_agent.py` — Chainlit app. Chat settings (model select + wiki page text input) trigger
  `setup_agent`, which builds the index and a ReActAgent with a "Wikipedia" QueryEngineTool.
  The agent is stored per user in `cl.user_session` under "agent".
- `utils.py` — `get_apikey()` reads the OpenAI key from `apikeys.yml`.

## Setup
- Requires Python 3.12: chainlit calls `nest_asyncio.apply()` on startup, which breaks async
  on newer Python (3.15 crashes with `NoEventLoopError` / "Timeout should be used inside a
  task", leaving a blank page).
- `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Create `apikeys.yml` (gitignored) in the project root:
  ```yaml
  openai:
    api_key: <your OpenAI key>
  ```

## Running
- `source .venv/bin/activate`
- App: `chainlit run chat_agent.py` (add `-w` to reload on save)
- Indexing only: `python index_wikipages.py`

## Gotchas
- Never print, log, or commit `apikeys.yml`.
- Pinned versions: llama-index 0.12.52, chainlit 2.11.0. Use `gpt-4o-mini`: the default
  gpt-3.5-turbo is deprecated and this llama-index doesn't support gpt-5 models.
- Chainlit 2.x imports from `chainlit.input_widget` (older versions: `input_widgets`), and
  `@cl.on_message` handlers receive a `cl.Message`; pass `message.content` to the agent.
- WikipediaReader needs `auto_suggest=False` ("paris" otherwise becomes "parks") and a custom
  user agent to avoid rate limits.
