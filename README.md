# AutoTuber

A Python pipeline for producing history-themed YouTube Shorts. It prepares a script and voiceover, renders video with FFmpeg, and uploads through the YouTube Data API. The repository also contains dashboard and scheduling utilities.

## Setup

Follow [SETUP.md](SETUP.md) for YouTube OAuth setup and repository secrets. Use the actual workflow file, [.github/workflows/pipeline.yml](.github/workflows/pipeline.yml), as the reference for its name and schedule.

The workflow is currently disabled manually. It can be run or re-enabled from GitHub Actions after its required secrets are configured. This README does not enable publishing or change its schedule.

## Local requirements

- Python 3.11
- FFmpeg and the system dependencies listed in the workflow
- Dependencies from `requirements.txt`
- Provider credentials configured outside source control

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`python main.py` runs the publishing pipeline and can upload to YouTube. Configure credentials and review the workflow before running it.

## Repository layout

- `pipeline/`: script, voice, subtitles, video, thumbnail, and upload stages
- `main.py`: pipeline entry point
- `setup/setup_youtube.py`: YouTube OAuth setup helper
- `dashboard/`: dashboard source
- `.github/workflows/pipeline.yml`: scheduled workflow

## License

[MIT](LICENSE).
