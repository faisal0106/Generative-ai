from __future__ import annotations

import json
import os
import re
from datetime import datetime
from html import escape
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from google import genai


load_dotenv()

APP_TITLE = "Flavor Fusion"
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CUISINES = [
    "Any",
    "Indian",
    "Italian",
    "Japanese",
    "Mexican",
    "French",
    "Mediterranean",
    "Thai",
    "Korean",
    "Middle Eastern",
]

DIETARY_OPTIONS = [
    "Vegetarian",
    "Vegan",
    "High protein",
    "Low carb",
    "Gluten free",
    "Dairy free",
    "Nut free",
    "Kid friendly",
]

MEAL_TYPES = [
    "Dinner",
    "Lunch",
    "Breakfast",
    "Snack",
    "Dessert",
    "Meal prep",
    "Party platter",
]

MOODS = [
    "Cozy",
    "Fresh",
    "Restaurant style",
    "Healthy",
    "Festive",
    "Budget friendly",
    "Quick comfort",
]


def init_state() -> None:
    st.session_state.setdefault("recipes", [])
    st.session_state.setdefault("favorites", [])
    st.session_state.setdefault("active_recipe", None)


def make_client() -> genai.Client | None:
    if not GOOGLE_API_KEY:
        return None
    return genai.Client(api_key=GOOGLE_API_KEY)


def strip_json(raw: str) -> dict[str, Any]:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def recipe_prompt(
    topic: str,
    cuisine: str,
    dietary: list[str],
    meal_type: str,
    mood: str,
    skill_level: str,
    servings: int,
    max_minutes: int,
    pantry: str,
    spice_level: int,
    detail_level: str,
) -> str:
    pantry_line = pantry.strip() or "No pantry ingredients were provided."
    diet_line = ", ".join(dietary) if dietary else "No dietary restrictions."

    return f"""
You are a practical professional chef and recipe developer.

Create a flexible recipe for: {topic}

Preferences:
- Cuisine: {cuisine}
- Meal type: {meal_type}
- Mood: {mood}
- Dietary needs: {diet_line}
- Cook skill level: {skill_level}
- Servings: {servings}
- Maximum total time: {max_minutes} minutes
- Spice level from 0 to 5: {spice_level}
- Pantry ingredients to prioritize: {pantry_line}
- Detail level: {detail_level}

Return only valid JSON with this exact shape:
{{
  "title": "Recipe title",
  "tagline": "Short appetizing line",
  "intro": "2 short sentences",
  "prep_time": "10 mins",
  "cook_time": "20 mins",
  "total_time": "30 mins",
  "servings": {servings},
  "difficulty": "{skill_level}",
  "ingredients": [
    {{"amount": "1 cup", "item": "ingredient", "category": "Produce"}}
  ],
  "steps": [
    {{"title": "Step name", "detail": "Clear cooking instruction", "time": "5 mins", "tip": "Optional tip"}}
  ],
  "substitutions": [
    {{"swap": "ingredient", "with": "alternative", "note": "why it works"}}
  ],
  "nutrition_notes": ["Short nutrition or balance note"],
  "plating": "Serving and garnish suggestion",
  "storage": "Storage and reheating advice",
  "shopping_list": ["item to buy"]
}}

Rules:
- Include 8 to 14 ingredients.
- Include 5 to 8 steps.
- Keep the recipe realistic for the requested time and skill level.
- If pantry ingredients are provided, use several of them naturally.
- Do not include markdown, code fences, comments, or text outside JSON.
"""


def generate_recipe(**kwargs: Any) -> dict[str, Any]:
    client = make_client()
    if client is None:
        raise RuntimeError("Missing GOOGLE_API_KEY. Add it to your .env file.")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=recipe_prompt(**kwargs),
    )
    data = strip_json(response.text or "")
    data["created_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
    data["request"] = kwargs
    return data


def css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg: #101511;
  --panel: rgba(255,255,255,0.055);
  --panel-strong: rgba(255,255,255,0.085);
  --line: rgba(255,255,255,0.13);
  --text: #f2eee6;
  --muted: rgba(242,238,230,0.66);
  --faint: rgba(242,238,230,0.42);
  --gold: #d9b66f;
  --gold-soft: #ffe2a6;
  --sage: #8ab48c;
  --tomato: #e06b5f;
  --berry: #b85b7d;
  --sky: #7fc5d6;
  --ink: #172019;
}

html, body, [class*="css"] {
  background:
    linear-gradient(120deg, rgba(217,182,111,0.06), transparent 22rem),
    radial-gradient(ellipse at 8% 8%, rgba(138,180,140,0.22), transparent 34rem),
    radial-gradient(ellipse at 85% 18%, rgba(127,197,214,0.14), transparent 28rem),
    radial-gradient(ellipse at 74% 90%, rgba(224,107,95,0.16), transparent 30rem),
    linear-gradient(135deg, #101511, #172019 54%, #111816) !important;
  color: var(--text) !important;
  font-family: Inter, sans-serif !important;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.32;
  background-image:
    linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
    repeating-linear-gradient(115deg, transparent 0 42px, rgba(217,182,111,0.035) 42px 43px);
  background-size: 46px 46px, 46px 46px, auto;
  mask-image: linear-gradient(to bottom, #000, transparent 92%);
  animation: textureDrift 18s linear infinite;
}

body::after {
  content: "";
  position: fixed;
  inset: -45%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.18;
  background:
    conic-gradient(from 140deg at 50% 50%, transparent, rgba(217,182,111,0.28), transparent, rgba(138,180,140,0.22), transparent);
  animation: slowTurn 28s linear infinite;
}

@keyframes textureDrift {
  from { background-position: 0 0, 0 0, 0 0; }
  to { background-position: 46px 46px, -46px 46px, 180px 0; }
}

@keyframes slowTurn {
  from { transform: rotate(0deg) scale(1); }
  to { transform: rotate(360deg) scale(1.04); }
}

#MainMenu, header, footer { visibility: hidden; }
.stApp { position: relative; overflow-x: hidden; }
.stApp > div { position: relative; z-index: 1; }
.block-container { max-width: 1240px; padding: 2.2rem 2rem 4rem !important; animation: pageRise 0.65s ease both; }

@keyframes pageRise {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

h1, h2, h3 {
  font-family: "Cormorant Garamond", serif !important;
  letter-spacing: 0 !important;
}

.hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 310px;
  gap: 2rem;
  align-items: center;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 8px;
  padding: 1.6rem;
  margin-bottom: 1.5rem;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.025)),
    linear-gradient(90deg, rgba(217,182,111,0.10), transparent 52%);
  box-shadow: 0 24px 90px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.12);
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0 28%, rgba(255,255,255,0.12) 38%, transparent 48% 100%);
  transform: translateX(-80%);
  animation: heroSweep 7s ease-in-out infinite;
}

.hero::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--gold), var(--sage), var(--sky), var(--tomato), var(--gold));
  background-size: 260% 100%;
  animation: borderFlow 5s linear infinite;
}

@keyframes heroSweep {
  0%, 45% { transform: translateX(-82%); }
  75%, 100% { transform: translateX(92%); }
}

@keyframes borderFlow {
  from { background-position: 0 0; }
  to { background-position: 260% 0; }
}

.hero-copy { position: relative; z-index: 1; }

.hero-stage {
  position: relative;
  z-index: 1;
  min-height: 250px;
  display: grid;
  place-items: center;
}

.eyebrow {
  color: var(--gold);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.hero h1 {
  font-size: clamp(3rem, 7vw, 5.8rem) !important;
  line-height: 0.92 !important;
  margin: 0.2rem 0 0.6rem !important;
  width: fit-content;
  color: transparent !important;
  background: linear-gradient(90deg, var(--text), var(--gold-soft), var(--sage), var(--text));
  background-size: 260% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  filter: drop-shadow(0 12px 28px rgba(0,0,0,0.34));
  animation: titleGlow 6s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% { background-position: 0 0; }
  50% { background-position: 100% 0; }
}

.hero p {
  color: var(--muted);
  max-width: 680px;
  font-size: 1rem;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.accent-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: rgba(242,238,230,0.78);
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.055);
  border-radius: 999px;
  padding: 0.34rem 0.72rem;
  font-size: 0.78rem;
}

.plate {
  position: relative;
  width: min(76vw, 245px);
  aspect-ratio: 1;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 48%, rgba(255,255,255,0.18) 0 18%, transparent 19%),
    radial-gradient(circle at 50% 50%, #1e2f22 0 43%, #f1ddaa 44% 46%, #25392a 47% 64%, rgba(255,255,255,0.11) 65% 66%, rgba(255,255,255,0.045) 67%);
  border: 1px solid rgba(255,255,255,0.16);
  box-shadow: 0 28px 80px rgba(0,0,0,0.38), inset 0 0 28px rgba(255,255,255,0.08);
  animation: plateFloat 5s ease-in-out infinite;
}

.plate::before,
.plate::after {
  content: "";
  position: absolute;
  left: 50%;
  width: 2px;
  height: 84px;
  border-radius: 99px;
  background: linear-gradient(to top, transparent, rgba(245,221,176,0.78), transparent);
  filter: blur(0.4px);
  transform-origin: bottom center;
  animation: steam 3.6s ease-in-out infinite;
}

.plate::before { top: -26px; transform: translateX(-34px) rotate(-10deg); }
.plate::after { top: -36px; transform: translateX(38px) rotate(9deg); animation-delay: 0.7s; }

.garnish {
  position: absolute;
  border-radius: 999px;
  background: var(--sage);
  box-shadow: 0 0 22px rgba(138,180,140,0.44);
}

.g1 { width: 46px; height: 9px; left: 66px; top: 82px; transform: rotate(-25deg); animation: garnishWiggle 4s ease-in-out infinite; }
.g2 { width: 54px; height: 10px; right: 55px; bottom: 82px; transform: rotate(22deg); animation: garnishWiggle 4.2s ease-in-out infinite reverse; }
.g3 { width: 12px; height: 12px; left: 118px; bottom: 66px; background: var(--tomato); animation: dotPop 2.7s ease-in-out infinite; }
.g4 { width: 10px; height: 10px; right: 98px; top: 74px; background: var(--gold); animation: dotPop 3.1s ease-in-out infinite 0.45s; }

@keyframes plateFloat {
  0%, 100% { transform: translateY(0) rotate(-2deg); }
  50% { transform: translateY(-12px) rotate(2deg); }
}

@keyframes steam {
  0% { opacity: 0; translate: 0 18px; scale: 0.94; }
  35% { opacity: 0.8; }
  100% { opacity: 0; translate: 0 -26px; scale: 1.1; }
}

@keyframes garnishWiggle {
  0%, 100% { translate: 0 0; }
  50% { translate: 4px -3px; }
}

@keyframes dotPop {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.28); opacity: 1; }
}

.panel {
  position: relative;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 1.2rem;
  box-shadow: 0 18px 60px rgba(0,0,0,0.24);
  overflow: hidden;
  min-height: 190px;
  transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
  animation: cardIn 0.65s ease both;
}

.panel::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent, rgba(255,255,255,0.08), transparent);
  transform: translateX(-105%);
  transition: transform 0.55s ease;
}

.panel::after {
  content: "";
  position: absolute;
  left: 1.2rem;
  right: 1.2rem;
  bottom: 1rem;
  height: 2px;
  background: linear-gradient(90deg, var(--gold), transparent);
  opacity: 0.55;
}

.panel:hover {
  transform: translateY(-7px);
  border-color: rgba(217,182,111,0.42);
  box-shadow: 0 30px 90px rgba(0,0,0,0.34), 0 0 36px rgba(217,182,111,0.09);
}

.panel:hover::before { transform: translateX(105%); }

.panel h3 {
  font-size: 1.75rem !important;
  margin: 0.25rem 0 0.7rem !important;
}

.panel-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  margin-bottom: 0.8rem;
  color: #111712;
  font-weight: 900;
  background: linear-gradient(135deg, var(--gold), var(--sage));
  box-shadow: 0 12px 34px rgba(217,182,111,0.22);
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}

.recipe-card {
  position: relative;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(0,0,0,0.25);
  animation: recipeReveal 0.55s ease both;
}

.recipe-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(217,182,111,0.14), transparent 42%),
    repeating-linear-gradient(135deg, transparent 0 26px, rgba(255,255,255,0.035) 26px 27px);
  pointer-events: none;
}

.recipe-card > * { position: relative; z-index: 1; }

@keyframes recipeReveal {
  from { opacity: 0; transform: translateY(14px) scale(0.99); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.recipe-title {
  font-family: "Cormorant Garamond", serif;
  font-size: 2.35rem;
  line-height: 1;
  margin-bottom: 0.2rem;
  color: var(--gold-soft);
}

.tagline {
  color: var(--gold);
  font-size: 1rem;
  margin-bottom: 0.7rem;
}

.muted { color: var(--muted); }
.faint { color: var(--faint); }

.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 0.8rem 0 0;
}

.pill {
  border: 1px solid rgba(217,182,111,0.3);
  background: rgba(217,182,111,0.09);
  color: #f5ddb0;
  border-radius: 999px;
  padding: 0.28rem 0.65rem;
  font-size: 0.78rem;
  transition: transform 0.18s ease, background 0.18s ease;
}

.pill:hover {
  transform: translateY(-2px);
  background: rgba(217,182,111,0.16);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.65rem;
  margin-top: 0.9rem;
}

.mini-metric {
  background: rgba(255,255,255,0.055);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.65rem;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.mini-metric:hover {
  transform: translateY(-3px);
  border-color: rgba(217,182,111,0.35);
}

.mini-metric b {
  display: block;
  color: var(--gold);
  font-size: 0.95rem;
}

.mini-metric span {
  color: var(--faint);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.item-row {
  position: relative;
  display: flex;
  gap: 0.55rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding: 0.5rem 0;
  transition: transform 0.18s ease, color 0.18s ease;
}

.item-row:hover {
  transform: translateX(6px);
}

.item-row::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-top: 0.45rem;
  background: var(--sage);
  box-shadow: 0 0 14px rgba(138,180,140,0.46);
}

.amount {
  color: var(--gold);
  min-width: 88px;
  font-weight: 700;
}

.step {
  position: relative;
  border-left: 3px solid var(--sage);
  background: rgba(138,180,140,0.08);
  border-radius: 0 8px 8px 0;
  padding: 0.9rem 1rem;
  margin-bottom: 0.75rem;
  overflow: hidden;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
  animation: stepSlide 0.5s ease both;
}

.step::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(217,182,111,0.12), transparent);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.step:hover {
  transform: translateX(6px);
  background: rgba(138,180,140,0.13);
  border-color: var(--gold);
}

.step:hover::after { opacity: 1; }
.step > * { position: relative; z-index: 1; }

@keyframes stepSlide {
  from { opacity: 0; transform: translateX(-14px); }
  to { opacity: 1; transform: translateX(0); }
}

.step b { color: var(--text); }
.step small { color: var(--gold); font-weight: 700; }

.stButton > button {
  border-radius: 8px !important;
  border: 1px solid rgba(217,182,111,0.45) !important;
  background: linear-gradient(135deg, #d9b66f, #8ab48c) !important;
  color: #111712 !important;
  font-weight: 800 !important;
  box-shadow: 0 12px 30px rgba(0,0,0,0.22), 0 0 0 rgba(217,182,111,0) !important;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
}

.stButton > button:hover {
  border-color: rgba(255,255,255,0.7) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 18px 40px rgba(0,0,0,0.28), 0 0 26px rgba(217,182,111,0.18) !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div, .stNumberInput input {
  background: rgba(255,255,255,0.065) !important;
  border-color: rgba(255,255,255,0.14) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease !important;
}

.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
  border-color: rgba(217,182,111,0.58) !important;
  box-shadow: 0 0 0 3px rgba(217,182,111,0.12) !important;
}

label, .stSlider label, .stSelectbox label, .stMultiSelect label,
.stTextInput label, .stTextArea label, .stRadio label, .stNumberInput label {
  color: var(--muted) !important;
  font-weight: 700 !important;
}

[data-testid="stExpander"] {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--line);
  border-radius: 8px;
}

[data-testid="stSidebar"] {
  background:
    linear-gradient(180deg, rgba(255,255,255,0.075), rgba(255,255,255,0.035)),
    linear-gradient(135deg, rgba(217,182,111,0.08), transparent) !important;
  border-right: 1px solid rgba(255,255,255,0.12);
}

[data-testid="stSidebar"]::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(120deg, transparent 0 34px, rgba(255,255,255,0.04) 34px 35px);
  opacity: 0.55;
}

[data-testid="stTabs"] button {
  border-radius: 8px !important;
}

.section-divider {
  height: 1px;
  margin: 1.1rem 0;
  background: linear-gradient(90deg, transparent, rgba(217,182,111,0.56), rgba(138,180,140,0.46), transparent);
  position: relative;
}

.section-divider::after {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gold);
  transform: translate(-50%, -50%);
  box-shadow: 0 0 18px rgba(217,182,111,0.75);
}

.stAlert {
  border-radius: 8px !important;
  border: 1px solid rgba(217,182,111,0.25) !important;
}

@media (max-width: 760px) {
  .block-container { padding: 1.2rem 1rem 3rem !important; }
  .hero { grid-template-columns: 1fr; padding: 1.15rem; }
  .hero-stage { min-height: 205px; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .recipe-title { font-size: 1.9rem; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
  }
}
</style>
""",
        unsafe_allow_html=True,
    )


def markdown_recipe(recipe: dict[str, Any]) -> str:
    ingredients = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])
    substitutions = recipe.get("substitutions", [])
    notes = recipe.get("nutrition_notes", [])

    lines = [
        f"# {recipe.get('title', 'Recipe')}",
        "",
        recipe.get("tagline", ""),
        "",
        f"Prep: {recipe.get('prep_time', '-')}",
        f"Cook: {recipe.get('cook_time', '-')}",
        f"Total: {recipe.get('total_time', '-')}",
        f"Servings: {recipe.get('servings', '-')}",
        f"Difficulty: {recipe.get('difficulty', '-')}",
        "",
        "## Ingredients",
    ]

    for item in ingredients:
        amount = item.get("amount", "")
        name = item.get("item", "")
        lines.append(f"- {amount} {name}".strip())

    lines.extend(["", "## Steps"])
    for index, step in enumerate(steps, start=1):
        time = f" ({step.get('time')})" if step.get("time") else ""
        lines.append(f"{index}. {step.get('title', 'Step')}{time}: {step.get('detail', '')}")
        if step.get("tip"):
            lines.append(f"   Tip: {step.get('tip')}")

    if substitutions:
        lines.extend(["", "## Substitutions"])
        for sub in substitutions:
            lines.append(f"- Swap {sub.get('swap')} with {sub.get('with')}: {sub.get('note')}")

    if notes:
        lines.extend(["", "## Nutrition Notes"])
        lines.extend(f"- {note}" for note in notes)

    lines.extend(
        [
            "",
            "## Plating",
            recipe.get("plating", ""),
            "",
            "## Storage",
            recipe.get("storage", ""),
        ]
    )
    return "\n".join(lines).strip()


def render_recipe(recipe: dict[str, Any]) -> None:
    title = escape(str(recipe.get("title", "Recipe")))
    tagline = escape(str(recipe.get("tagline", "")))
    intro = escape(str(recipe.get("intro", "")))
    request = recipe.get("request", {})
    dietary = request.get("dietary", [])

    st.markdown(
        f"""
<div class="recipe-card">
  <div class="recipe-title">{title}</div>
  <div class="tagline">{tagline}</div>
  <div class="muted">{intro}</div>
  <div class="pill-row">
    <span class="pill">{escape(str(request.get("cuisine", "Any")))}</span>
    <span class="pill">{escape(str(request.get("meal_type", "Meal")))}</span>
    <span class="pill">{escape(str(request.get("mood", "Balanced")))}</span>
    <span class="pill">Spice {escape(str(request.get("spice_level", 0)))}/5</span>
    {"".join(f'<span class="pill">{escape(str(item))}</span>' for item in dietary)}
  </div>
  <div class="metric-grid">
    <div class="mini-metric"><b>{escape(str(recipe.get("prep_time", "-")))}</b><span>Prep</span></div>
    <div class="mini-metric"><b>{escape(str(recipe.get("cook_time", "-")))}</b><span>Cook</span></div>
    <div class="mini-metric"><b>{escape(str(recipe.get("total_time", "-")))}</b><span>Total</span></div>
    <div class="mini-metric"><b>{escape(str(recipe.get("servings", "-")))}</b><span>Serves</span></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    tab_recipe, tab_shopping, tab_flex, tab_export = st.tabs(
        ["Recipe", "Shopping List", "Flexible Swaps", "Export"]
    )

    with tab_recipe:
        left, right = st.columns([0.9, 1.15], gap="large")
        with left:
            st.subheader("Ingredients")
            for item in recipe.get("ingredients", []):
                st.markdown(
                    f"""
<div class="item-row">
  <div class="amount">{escape(str(item.get("amount", "")))}</div>
  <div>{escape(str(item.get("item", "")))}<br><span class="faint">{escape(str(item.get("category", "")))}</span></div>
</div>
""",
                    unsafe_allow_html=True,
                )

        with right:
            st.subheader("Method")
            for index, step in enumerate(recipe.get("steps", []), start=1):
                st.markdown(
                    f"""
<div class="step">
  <small>STEP {index} {escape(str(step.get("time", "")))}</small><br>
  <b>{escape(str(step.get("title", "Step")))}</b>
  <div class="muted">{escape(str(step.get("detail", "")))}</div>
  {f'<div class="tagline">Tip: {escape(str(step.get("tip")))}</div>' if step.get("tip") else ""}
</div>
""",
                    unsafe_allow_html=True,
                )

        st.info(recipe.get("plating", ""))
        st.caption(recipe.get("storage", ""))

    with tab_shopping:
        shopping = recipe.get("shopping_list") or [
            item.get("item", "") for item in recipe.get("ingredients", [])
        ]
        checked = []
        for item in shopping:
            if st.checkbox(str(item), key=f"shop-{title}-{item}"):
                checked.append(str(item))
        st.caption(f"{len(checked)} of {len(shopping)} items checked")

    with tab_flex:
        st.subheader("Substitutions")
        for sub in recipe.get("substitutions", []):
            st.markdown(
                f"- **{escape(str(sub.get('swap', 'Swap')))}** -> "
                f"**{escape(str(sub.get('with', 'Alternative')))}**: "
                f"{escape(str(sub.get('note', '')))}"
            )

        st.subheader("Nutrition Notes")
        for note in recipe.get("nutrition_notes", []):
            st.markdown(f"- {escape(str(note))}")

    with tab_export:
        recipe_md = markdown_recipe(recipe)
        file_name = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "recipe"
        st.download_button(
            "Download recipe as Markdown",
            data=recipe_md,
            file_name=f"{file_name}.md",
            mime="text/markdown",
        )
        st.code(recipe_md, language="markdown")


def render_history() -> None:
    if not st.session_state.recipes:
        st.caption("Generated recipes will appear here during this session.")
        return

    for index, recipe in enumerate(reversed(st.session_state.recipes[-6:]), start=1):
        actual_index = len(st.session_state.recipes) - index
        title = recipe.get("title", "Recipe")
        created = recipe.get("created_at", "")
        cols = st.columns([1, 0.35, 0.35], gap="small")
        cols[0].markdown(f"**{title}**  \n<span class='faint'>{created}</span>", unsafe_allow_html=True)
        if cols[1].button("Open", key=f"open-{actual_index}"):
            st.session_state.active_recipe = recipe
        if cols[2].button("Save", key=f"save-{actual_index}"):
            if recipe not in st.session_state.favorites:
                st.session_state.favorites.append(recipe)


def main() -> None:
    st.set_page_config(
        page_title=f"{APP_TITLE} - AI Recipe Studio",
        page_icon="FF",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_state()
    css()

    st.markdown(
        """
<section class="hero">
  <div class="hero-copy">
    <div class="eyebrow">AI Recipe Studio</div>
    <h1>Flavor Fusion</h1>
    <p>Design recipes around your cravings, pantry, time, diet, spice level, and cooking confidence. Save the good ones, export them, and turn dinner decisions into something much less exhausting.</p>
    <div class="hero-actions">
      <span class="accent-chip">Pantry aware</span>
      <span class="accent-chip">Animated method cards</span>
      <span class="accent-chip">Export ready</span>
    </div>
  </div>
  <div class="hero-stage" aria-hidden="true">
    <div class="plate">
      <span class="garnish g1"></span>
      <span class="garnish g2"></span>
      <span class="garnish g3"></span>
      <span class="garnish g4"></span>
    </div>
  </div>
</section>
""",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.subheader("Studio")
        topic = st.text_input("Dish or craving", placeholder="Paneer tacos, lemon pasta, millet bowl")
        meal_type = st.selectbox("Meal type", MEAL_TYPES)
        cuisine = st.selectbox("Cuisine direction", CUISINES)
        mood = st.selectbox("Style", MOODS)
        dietary = st.multiselect("Dietary preferences", DIETARY_OPTIONS)

        st.divider()
        servings = st.number_input("Servings", min_value=1, max_value=12, value=4)
        max_minutes = st.slider("Maximum total time", 10, 180, 45, 5)
        spice_level = st.slider("Spice level", 0, 5, 2)
        skill_level = st.radio("Skill level", ["Beginner", "Confident", "Advanced"], horizontal=True)
        detail_level = st.radio("Detail", ["Concise", "Guided", "Chef notes"], horizontal=True)
        pantry = st.text_area(
            "Pantry ingredients",
            placeholder="tomatoes, curd, rice, spinach, chickpeas",
            height=92,
        )

        generate = st.button("Create Recipe", disabled=not topic.strip(), use_container_width=True)

        st.divider()
        st.subheader("History")
        render_history()

        if st.session_state.favorites:
            with st.expander("Favorites", expanded=False):
                for favorite in st.session_state.favorites[-5:]:
                    st.write(favorite.get("title", "Recipe"))

    if generate:
        with st.spinner("Building a flexible recipe..."):
            try:
                recipe = generate_recipe(
                    topic=topic.strip(),
                    cuisine=cuisine,
                    dietary=dietary,
                    meal_type=meal_type,
                    mood=mood,
                    skill_level=skill_level,
                    servings=int(servings),
                    max_minutes=int(max_minutes),
                    pantry=pantry,
                    spice_level=int(spice_level),
                    detail_level=detail_level,
                )
                st.session_state.recipes.append(recipe)
                st.session_state.active_recipe = recipe
            except Exception as exc:
                st.error(str(exc))

    if st.session_state.active_recipe:
        render_recipe(st.session_state.active_recipe)
    else:
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            st.markdown(
                '<div class="panel"><div class="panel-icon">1</div><div class="eyebrow">Flexible</div><h3>Cook around real life</h3><p class="muted">Tune time, servings, skill level, pantry ingredients, spice, diet, and cuisine before generating.</p></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                '<div class="panel"><div class="panel-icon">2</div><div class="eyebrow">Useful</div><h3>Shop and substitute</h3><p class="muted">Every recipe includes a checklist, flexible swaps, nutrition notes, plating, storage, and reheating guidance.</p></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                '<div class="panel"><div class="panel-icon">3</div><div class="eyebrow">Reusable</div><h3>Save the good ideas</h3><p class="muted">Generated recipes stay in session history, can be favorited, reopened, and downloaded as Markdown.</p></div>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
