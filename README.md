# Databricks Weekly Digest

Automated weekly digest of Databricks developments, delivered as a written summary and a two-host podcast.

## What it does

1. **Aggregates** content from Databricks blog, YouTube channels, and release notes
2. **Summarizes** with Gemini into a structured digest focused on what matters to data engineers
3. **Generates a podcast** with two AI hosts discussing the highlights (Gemini TTS)
4. **Distributes** via email, Teams, and/or Confluence (configurable)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
cp .env.example .env
# Edit .env with your key from aistudio.google.com

# Run the full pipeline
python run.py

# Just the written digest (no podcast)
python run.py --skip-podcast

# Generate podcast from an existing digest
python run.py --from-digest output/2026-03-14/digest.md
```

## Configuration

Edit `config.yaml` to customize:

- **YouTube channels** to track
- **Podcast hosts** names, voices, and personalities
- **Distribution** channels (email, Teams, Confluence)
- **Lookback window** (default: 7 days)

## Credentials

Only one credential needed: a **Gemini API key** from [Google AI Studio](https://aistudio.google.com).

For distribution (optional):
- **Gmail**: App Password (Settings > Security > App Passwords)
- **Teams**: Incoming Webhook URL
- **Confluence**: Cloud ID + Space ID (works with Atlassian MCP in Cursor)

## Output

Each run creates a dated folder in `output/`:
```
output/2026-03-14/
  digest.md            # Written digest
  podcast_script.txt   # Two-host dialogue script
  podcast.wav          # Audio podcast
```

## Scheduling

Run weekly via:
- **Databricks Workflow**: Add as a Python task
- **GitHub Actions**: Cron schedule
- **Task Scheduler** (Windows): Point at `run.py`
