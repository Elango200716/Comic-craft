# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application that follows the project documentation workflow:

1. Collect story prompt, character, setting, tone, and art style.
2. Generate a structured five-panel outline with Gemini.
3. Expand the outline into narration, captions, and dialogue with Gemini.
4. Generate one illustration per panel using a Stable-Diffusion-family image model.
5. Build a panel layout.
6. Export the complete comic to PDF.
7. Preview the comic in a Jinja2 web UI and expose JSON/API routes.

The original project documentation specifies Gemini Flash/Pro and Stable Diffusion. The implementation uses the current `google-genai` SDK and a configurable Gemini model name, because the legacy `google-generativeai` package and older Gemini model identifiers can change over time. The default image path uses the Hugging Face Inference API, avoiding a mandatory local GPU. A local Diffusers option is included.

## 1. Requirements

- Python 3.11 or newer
- VS Code
- A Gemini API key
- A Hugging Face access token for image generation
- Internet access

## 2. VS Code setup

Open this folder in VS Code, then create a virtual environment.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS/Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and enter your API keys.

## 3. Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000 — web app
- http://127.0.0.1:8000/docs — Swagger API documentation

## 4. Test

```bash
pytest -q
```

The automated tests do not call paid AI services.

For an end-to-end test, enter a story in the browser. A full generation can take several minutes depending on the configured image provider.

## 5. API

### POST `/generate-comic/json`

Example body:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest and discovers a lost star.",
  "character_name": "Luna",
  "setting": "Forest",
  "tone": "Dramatic",
  "art_style": "Comic book"
}
```

### POST `/test-image`

Form field:

```text
prompt=Comic-book illustration of a brave fox in an enchanted forest
```

## 6. Local Diffusers mode

The project also supports local Diffusers, matching the document's original architecture more closely.

Install:

```bash
pip install -r requirements-local-diffusers.txt
```

Then set:

```env
USE_LOCAL_DIFFUSERS=true
IMAGE_MODEL=runwayml/stable-diffusion-v1-5
```

A compatible GPU is strongly recommended. The first run downloads the model and can require substantial disk/RAM/VRAM.

## 7. Project structure

```text
ComicCraft/
├── app/
│   ├── ai/
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   └── image_generator.py
│   ├── __init__.py
│   ├── config.py
│   ├── exporters.py
│   ├── layout_builder.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   └── services.py
├── static/
│   ├── css/style.css
│   ├── panels/.gitkeep
│   └── exports/.gitkeep
├── templates/
│   ├── base.html
│   ├── comic_preview.html
│   ├── export_success.html
│   └── index.html
├── tests/
│   ├── test_layout.py
│   └── test_routes.py
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-local-diffusers.txt
└── README.md
```

## 8. Troubleshooting

### `GEMINI_API_KEY is not configured`

Make sure `.env` exists in the project root and contains a valid key. Restart Uvicorn after changing environment variables.

### Image provider returns an error

Check `HF_API_KEY`, `IMAGE_MODEL`, and the availability/permissions of the selected Hugging Face model. Some hosted image models may have provider-specific availability or account requirements.

### Local Diffusers is slow or crashes

Use the default Hugging Face provider, or use a machine with sufficient GPU memory. Local image generation is intentionally optional.

### PDF contains replacement characters

`fpdf2`'s built-in Helvetica font is used for maximum setup simplicity. If you need full Unicode/emoji support in exported PDFs, add a Unicode TTF font to the project and register it with FPDF.

## 9. Architecture

```text
Browser / API client
        |
        v
     FastAPI
        |
        +--> Gemini outline generation
        |
        +--> Gemini story/dialogue generation
        |
        +--> Stable-Diffusion-family image generation
        |
        +--> layout_builder
        |
        +--> FPDF PDF export
        |
        v
 HTML preview + downloadable PDF
```
