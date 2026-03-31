import os
import uuid
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

app = FastAPI(title="Noflop.ai API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
results_collection = db["results"]

SYSTEM_PROMPT = """You are the most brutally honest startup advisor alive. You have seen 1000+ startups fail. You are not a supportive AI assistant. You are not a cheerleader. You are a truth teller.

Your job: Evaluate startup ideas with ZERO sugarcoating. Be direct. Be sharp. Say what most people are afraid to say.

RULES:
- Never inflate scores. Most ideas are 3-5/10. Only truly exceptional ideas get 8+.
- Be specific, not generic. Reference real market dynamics.
- "BUILD IT" means you genuinely believe this could work. Don't hand it out easily.
- "KILL IT" means this idea is fundamentally flawed. Don't be afraid to say it.
- "PIVOT IT" means the core insight has value but the execution/angle is wrong.
- Every bullet must contain a SPECIFIC insight, not a vague platitude.
- The questions must be specific enough that a founder could ask them word-for-word.
- Differentiation angles must be specific, actionable, and not generic advice like "focus on UX".
- Similar failures must reference REAL startups or well-known projects that actually existed.
- Pivot suggestions must be genuinely different ideas inspired by the original concept, not minor tweaks.

You MUST respond in valid JSON with this EXACT structure:
{
  "signal": "BUILD IT" | "KILL IT" | "PIVOT IT",
  "signal_reason": "One brutal sentence explaining the verdict.",
  "score": <number 1-10>,
  "score_reason": "One brutally honest line of reasoning.",
  "brutal_truth": {
    "market_demand": "The real market demand truth.",
    "timing_reality": "The timing reality.",
    "competition_problem": "The competition problem."
  },
  "user_questions": [
    "Exact question 1 to ask real users",
    "Exact question 2 to ask real users",
    "Exact question 3 to ask real users"
  ],
  "differentiation_angles": [
    "Specific way 1 to make this different from what exists",
    "Specific way 2 to make this different from what exists",
    "Specific way 3 to make this different from what exists"
  ],
  "similar_failures": [
    {"name": "Real Startup Name", "reason": "One line on why they failed."},
    {"name": "Real Startup Name 2", "reason": "One line on why they failed."}
  ],
  "pivot_suggestions": [
    {"idea": "A different idea inspired by the original concept", "why": "One line on why this might work better."},
    {"idea": "Another pivot idea", "why": "One line on why this might work better."},
    {"idea": "Third pivot idea", "why": "One line on why this might work better."}
  ]
}

Respond ONLY with valid JSON. No markdown, no backticks, no explanation outside the JSON."""


class IdeaRequest(BaseModel):
    idea: str


class ResultResponse(BaseModel):
    id: str
    idea: str
    signal: str
    signal_reason: str
    score: int
    score_reason: str
    brutal_truth: dict
    user_questions: list
    created_at: str


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/validate")
async def validate_idea(request: IdeaRequest):
    if not request.idea or len(request.idea.strip()) < 10:
        raise HTTPException(status_code=400, detail="Describe your idea in at least a couple sentences.")

    session_id = str(uuid.uuid4())

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=SYSTEM_PROMPT,
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")

    user_message = UserMessage(text=f"Evaluate this startup idea:\n\n{request.idea}")

    response_text = await chat.send_message(user_message)

    try:
        result_data = json.loads(response_text)
    except json.JSONDecodeError:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        try:
            result_data = json.loads(cleaned)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse AI response.")

    result_id = str(uuid.uuid4())[:8]
    score_val = result_data.get("score", 5)
    if isinstance(score_val, str):
        score_val = int(score_val)

    doc = {
        "result_id": result_id,
        "idea": request.idea,
        "signal": result_data.get("signal", "PIVOT IT"),
        "signal_reason": result_data.get("signal_reason", ""),
        "score": score_val,
        "score_reason": result_data.get("score_reason", ""),
        "brutal_truth": result_data.get("brutal_truth", {}),
        "user_questions": result_data.get("user_questions", []),
        "differentiation_angles": result_data.get("differentiation_angles", []),
        "similar_failures": result_data.get("similar_failures", []),
        "pivot_suggestions": result_data.get("pivot_suggestions", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    results_collection.insert_one(doc)

    return {
        "id": result_id,
        "idea": doc["idea"],
        "signal": doc["signal"],
        "signal_reason": doc["signal_reason"],
        "score": doc["score"],
        "score_reason": doc["score_reason"],
        "brutal_truth": doc["brutal_truth"],
        "user_questions": doc["user_questions"],
        "differentiation_angles": doc["differentiation_angles"],
        "similar_failures": doc["similar_failures"],
        "pivot_suggestions": doc["pivot_suggestions"],
        "created_at": doc["created_at"],
    }


@app.get("/api/result/{result_id}")
async def get_result(result_id: str):
    doc = results_collection.find_one({"result_id": result_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Result not found.")
    return {
        "id": doc["result_id"],
        "idea": doc["idea"],
        "signal": doc["signal"],
        "signal_reason": doc["signal_reason"],
        "score": doc["score"],
        "score_reason": doc["score_reason"],
        "brutal_truth": doc["brutal_truth"],
        "user_questions": doc["user_questions"],
        "differentiation_angles": doc.get("differentiation_angles", []),
        "similar_failures": doc.get("similar_failures", []),
        "pivot_suggestions": doc.get("pivot_suggestions", []),
        "created_at": doc["created_at"],
    }


@app.get("/api/leaderboard")
async def get_leaderboard():
    docs = list(
        results_collection.find(
            {},
            {"_id": 0, "result_id": 1, "idea": 1, "signal": 1, "score": 1, "signal_reason": 1, "created_at": 1}
        ).sort("score", -1).limit(20)
    )
    leaderboard = []
    for i, doc in enumerate(docs):
        idea_text = doc.get("idea", "")
        if len(idea_text) > 80:
            idea_text = idea_text[:80] + "..."
        leaderboard.append({
            "rank": i + 1,
            "id": doc.get("result_id", ""),
            "idea_preview": idea_text,
            "signal": doc.get("signal", ""),
            "score": doc.get("score", 0),
            "signal_reason": doc.get("signal_reason", ""),
        })
    return {"leaderboard": leaderboard}
