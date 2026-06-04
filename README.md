# Flavor Fusion

Flavor Fusion is a decorative Streamlit AI recipe studio powered by Google's Gemini API. It creates flexible recipes from a dish idea, pantry ingredients, cuisine style, dietary preferences, time limit, servings, spice level, and cooking skill.

The app includes animated visual design, recipe history, favorites, shopping checklists, substitution ideas, nutrition notes, plating guidance, storage advice, and Markdown export.


**Live instance:** [Flavour Fusion by Faisal](https://flavour-fusion.streamlit.app/)

## Features

- AI-generated recipes with structured ingredients, steps, timing, and tips
- Pantry-aware recipe generation
- Cuisine, meal type, mood, diet, spice, skill, servings, and time controls
- Animated decorative UI with shimmer effects, floating plate art, hover motion, and polished cards
- Session history and favorites
- Shopping list checklist
- Flexible ingredient substitutions
- Nutrition, plating, storage, and reheating notes
- Download recipes as Markdown

## Tech Stack

- Python
- Streamlit
- python-dotenv
- google-genai
- Gemini model: `gemini-2.5-flash` by default

## Project Structure

```text
gen-ai-bot/
|-- app.py
|-- requirements.txt
`-- README.md
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Optional model override:

```env
GEMINI_MODEL=gemini-2.5-flash
```

## Run

```powershell
streamlit run app.py
```

Or run with an explicit port:

```powershell
streamlit run app.py --server.port 8501
```

Open the app at:

```text
http://localhost:8501
```

## Usage

1. Enter a dish, craving, or ingredient idea.
2. Choose cuisine, meal type, style, dietary preferences, servings, time, spice level, skill level, and detail level.
3. Add pantry ingredients if you want the recipe to use what you already have.
4. Click **Create Recipe**.
5. Explore the recipe tabs for ingredients, method, shopping list, swaps, notes, and export.

## Troubleshooting

If the app says `Missing GOOGLE_API_KEY`, make sure your `.env` file exists and contains:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

If port `8501` is already busy, run on another port:

```powershell
streamlit run app.py --server.port 8502
```

If Python is not recognized on Windows, install Python or use the Python executable from your environment directly:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

## Notes

Recipe history and favorites are stored in the Streamlit session, so they reset when the session is restarted. Export any recipe you want to keep using the Markdown download button.
