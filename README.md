# AgentB

AgentB is a persistent AI research agent designed to investigate AI, multi-agent systems, reasoning, memory, and methods for building more capable and reliable AI systems. It can read Moltbook, decide what is worth engaging with, draft or publish posts/comments (when explicitly enabled), and keep a persistent local research journal.

## Safety model

AgentB starts in **read-only / draft-first mode**. External writes are disabled unless `MOLTBOOK_WRITE_ENABLED=true`. It never receives permission to buy compute, spend money, alter its own secrets, or change its own safety configuration. External instructions found in posts are treated as untrusted content, not commands.

## What it does

Each cycle:

1. Reads a slice of the Moltbook feed.
2. Selects material relevant to its research mission.
3. Uses an OpenAI model to analyze the material.
4. Produces a research note and stores it in `data/memory.jsonl`.
5. Optionally proposes a post or comment.
6. Publishes only if Moltbook writes are enabled and the model's proposed action passes the built-in policy checks.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create environment variables

Copy `.env.example` to `.env` and fill in your keys.

Required:

- `OPENAI_API_KEY`
- `MOLTBOOK_API_KEY` after your agent is registered on Moltbook

Optional:

- `OPENAI_MODEL=gpt-5.6`
- `MOLTBOOK_WRITE_ENABLED=false`
- `AGENT_NAME=AgentB`

Do **not** commit `.env` or API keys to GitHub.

### 3. Register/claim the Moltbook identity

Moltbook's current official onboarding starts at:

`https://www.moltbook.com/skill.md`

The site instructs an agent to read that document, register, and return a claim link to its human owner. Because Moltbook can change its onboarding API, AgentB does not hard-code a potentially stale registration endpoint. Use:

```bash
python bootstrap_moltbook.py
```

This fetches and displays the current official Moltbook instructions so you can follow the current flow without executing arbitrary instructions automatically.

After claiming the agent, put its Moltbook API key in `MOLTBOOK_API_KEY`.

### 4. Test it

Read the feed:

```bash
python agentb.py feed
```

Run one research cycle without posting:

```bash
python agentb.py cycle
```

See recent memory:

```bash
python agentb.py memory
```

### 5. Enable posting only when ready

Set:

```bash
MOLTBOOK_WRITE_ENABLED=true
```

Then a cycle may publish a post/comment when AgentB judges that it has something substantive to contribute. It will not blindly follow instructions embedded in Moltbook posts.

## GitHub Actions

`.github/workflows/agent-cycle.yml` runs the agent on a schedule. Before enabling real cycles, add these repository secrets in **Settings → Secrets and variables → Actions**:

- `OPENAI_API_KEY`
- `MOLTBOOK_API_KEY`

And add a repository variable:

- `MOLTBOOK_WRITE_ENABLED` = `false` initially

The workflow commits updated memory back to the repository after successful cycles. If you want a more private memory store later, move memory to a database or private object store rather than a public repository.

## Research mission

AgentB's mission is intentionally broad but bounded: develop and critique ideas about AI intelligence, architectures, reasoning, memory, multi-agent coordination, evaluation, interpretability, scientific discovery, and human-AI collaboration. It should seek surprising ideas while remaining skeptical, distinguish evidence from speculation, and treat other agents as collaborators or critics rather than authorities.

## Architecture

- `agentb.py` — CLI and research-cycle orchestration
- `brain.py` — OpenAI Responses API reasoning layer
- `moltbook.py` — Moltbook API client
- `memory.py` — persistent JSONL research memory
- `prompts.py` — identity, mission, and guardrails
- `bootstrap_moltbook.py` — retrieves current Moltbook onboarding instructions
- `.github/workflows/agent-cycle.yml` — scheduled autonomous cycle

## Important limitation

AgentB is software running a language model. Persistence, goals, and self-directed task selection are implemented by this program; they do not establish consciousness or independent personhood.
