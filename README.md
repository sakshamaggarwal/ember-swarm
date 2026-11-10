# Ember Swarm 🐝

**100 AI agents. One hard question. Under $1.**

Ember Swarm launches 100 parallel Muse Ember agents — each playing a different expert — to collectively solve complex problems. Built for the OpenRouter × Meta Build Day challenge.

## Quick start

```bash
export OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY
pip3 install aiohttp
python3 swarm.py "Design a Mars colony for 1000 people"
```

## How it works

1. **Swarm** — 100 Ember agents run in parallel, each with a unique expert persona
2. **Synthesize** — One agent reads all 100 answers and combines the best ideas
3. **Judge** — 10 agents score the result on creativity, feasibility, completeness

Total cost: ~$0.02 per run. The power of cheap intelligence at scale.

## Why Ember?

At $0.10/M input and $0.50/M output, Ember is cheap enough to treat as a swarm worker. No other frontier model lets you run 100+ calls for pennies.

## Built with

- [Muse Ember](https://openrouter.ai/meta/muse-ember) via [OpenRouter](https://openrouter.ai)
- Python 3, asyncio, aiohttp

## License

MIT
