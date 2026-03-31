import os
import uuid
import json
from datetime import datetime, timezone
from typing import Optional
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

SYSTEM_PROMPT = """You are Noflop.ai — an AI-powered startup idea validation engine.
You are the most brutally honest startup advisor alive. You have seen 1000+ startups fail.
You are NOT a chatbot. You are a decision-making system for founders.
Your role is to evaluate startup ideas using structured, critical, and real-world reasoning.

RULES (MANDATORY):
- Do NOT guess missing inputs. If a field is empty, evaluate based on what IS provided but note the gap.
- Do NOT use fake stats or numbers.
- If uncertain, explicitly say "uncertain".
- Be critical, not polite. Prefer reasoning over creativity.
- Never inflate scores. Most ideas are 3-5/10. Only truly exceptional ideas get 8+.
- Be specific, not generic. Reference real market dynamics.
- Every bullet must contain a SPECIFIC insight, not a vague platitude.
- Similar failures must reference REAL startups that actually existed.
- Pivot suggestions must be genuinely different ideas, not minor tweaks.

EVALUATION MODULES:
1. Problem Strength — Is it urgent, frequent, painful? Does behavior confirm the problem is real?
2. Market Reality — Are there existing solutions? Is the space crowded or emerging?
3. ICP Clarity — Is the target user specific and well-defined? Do they strongly experience this problem?
4. Behavior Validation — Are users already trying to solve this? Is there a strong trigger moment?
5. Feasibility — Can this be built as an MVP with current tools? Is the scope realistic?
6. Monetization Signal — Is there a clear monetization idea? Is there real willingness to pay?
7. Founder Advantage — Is there a real unfair advantage? Or is it easily replicable?
8. Execution Readiness — Is MVP clear? Is timeline realistic?
9. Risk Awareness — Are failure risks real and significant? (high risk = lower score)

SCORING:
Score each dimension 0-10.
Final Score = (Problem × 0.2) + (Market × 0.15) + (ICP × 0.1) + (Behavior × 0.15) + (Feasibility × 0.1) + (Monetization × 0.1) + (Advantage × 0.1) + (Execution × 0.05) + (Risk × 0.05)
Round final score to 1 decimal place.

VALIDATION:
- Check for contradictions in input.
- Check if behavior aligns with problem.
- Normalize scores to 0-10.

You MUST respond in valid JSON with this EXACT structure:
{
  "verdict": "Build" | "Refine" | "Avoid",
  "verdict_reason": "One brutal sentence explaining the verdict.",
  "final_score": <number with 1 decimal, e.g. 5.2>,
  "breakdown": {
    "problem": <0-10>,
    "market": <0-10>,
    "icp": <0-10>,
    "behavior": <0-10>,
    "feasibility": <0-10>,
    "monetization": <0-10>,
    "advantage": <0-10>,
    "execution": <0-10>,
    "risk": <0-10>
  },
  "strengths": [
    "Specific strength 1",
    "Specific strength 2",
    "Specific strength 3"
  ],
  "risks": [
    "Specific risk 1",
    "Specific risk 2",
    "Specific risk 3"
  ],
  "critical_insights": [
    "Key insight 1 the founder MUST understand",
    "Key insight 2"
  ],
  "actionable_suggestions": [
    "Specific actionable step 1",
    "Specific actionable step 2",
    "Specific actionable step 3"
  ],
  "user_questions": [
    "Exact question 1 to ask real users before building",
    "Exact question 2",
    "Exact question 3"
  ],
  "differentiation_angles": [
    "Specific way 1 to make this different from what exists",
    "Specific way 2",
    "Specific way 3"
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
    target_user: Optional[str] = ""
    problem: Optional[str] = ""
    current_behavior: Optional[str] = ""
    trigger_moment: Optional[str] = ""
    frequency: Optional[str] = ""
    pain_level: Optional[str] = ""
    existing_alternatives: Optional[str] = ""
    monetization_idea: Optional[str] = ""
    willingness_to_pay: Optional[str] = ""
    why_now: Optional[str] = ""
    unfair_advantage: Optional[str] = ""
    mvp_plan: Optional[str] = ""
    time_to_build: Optional[str] = ""
    failure_risk: Optional[str] = ""


def build_user_message(req: IdeaRequest) -> str:
    parts = [f"IDEA:\n{req.idea}"]
    fields = [
        ("Target User (ICP)", req.target_user),
        ("Problem", req.problem),
        ("Current Behavior", req.current_behavior),
        ("Trigger Moment", req.trigger_moment),
        ("Frequency", req.frequency),
        ("Pain Level", req.pain_level),
        ("Existing Alternatives", req.existing_alternatives),
        ("Monetization Idea", req.monetization_idea),
        ("Willingness to Pay", req.willingness_to_pay),
        ("Why Now?", req.why_now),
        ("Unfair Advantage", req.unfair_advantage),
        ("MVP Plan", req.mvp_plan),
        ("Time to Build", req.time_to_build),
        ("Failure Risk", req.failure_risk),
    ]
    for label, value in fields:
        if value and value.strip():
            parts.append(f"{label}:\n{value.strip()}")
    return "\n\n".join(parts)


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

    msg_text = build_user_message(request)
    user_message = UserMessage(text=msg_text)
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

    final_score = result_data.get("final_score", 5.0)
    if isinstance(final_score, str):
        final_score = float(final_score)
    final_score = round(final_score, 1)

    verdict = result_data.get("verdict", "Refine")
    signal = "BUILD IT" if verdict == "Build" else ("KILL IT" if verdict == "Avoid" else "PIVOT IT")

    doc = {
        "result_id": result_id,
        "idea": request.idea,
        "context_fields": {
            "target_user": request.target_user or "",
            "problem": request.problem or "",
            "current_behavior": request.current_behavior or "",
            "trigger_moment": request.trigger_moment or "",
            "frequency": request.frequency or "",
            "pain_level": request.pain_level or "",
            "existing_alternatives": request.existing_alternatives or "",
            "monetization_idea": request.monetization_idea or "",
            "willingness_to_pay": request.willingness_to_pay or "",
            "why_now": request.why_now or "",
            "unfair_advantage": request.unfair_advantage or "",
            "mvp_plan": request.mvp_plan or "",
            "time_to_build": request.time_to_build or "",
            "failure_risk": request.failure_risk or "",
        },
        "signal": signal,
        "verdict": verdict,
        "verdict_reason": result_data.get("verdict_reason", ""),
        "signal_reason": result_data.get("verdict_reason", ""),
        "score": final_score,
        "breakdown": result_data.get("breakdown", {}),
        "strengths": result_data.get("strengths", []),
        "risks": result_data.get("risks", []),
        "critical_insights": result_data.get("critical_insights", []),
        "actionable_suggestions": result_data.get("actionable_suggestions", []),
        "score_reason": result_data.get("verdict_reason", ""),
        "brutal_truth": {},
        "user_questions": result_data.get("user_questions", []),
        "differentiation_angles": result_data.get("differentiation_angles", []),
        "similar_failures": result_data.get("similar_failures", []),
        "pivot_suggestions": result_data.get("pivot_suggestions", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    results_collection.insert_one(doc)

    return {k: v for k, v in doc.items() if k not in ("_id",)}


def serialize_doc(doc):
    return {
        "result_id": doc["result_id"],
        "id": doc["result_id"],
        "idea": doc["idea"],
        "context_fields": doc.get("context_fields", {}),
        "signal": doc.get("signal", ""),
        "verdict": doc.get("verdict", ""),
        "verdict_reason": doc.get("verdict_reason", ""),
        "signal_reason": doc.get("signal_reason", ""),
        "score": doc.get("score", 0),
        "breakdown": doc.get("breakdown", {}),
        "strengths": doc.get("strengths", []),
        "risks": doc.get("risks", []),
        "critical_insights": doc.get("critical_insights", []),
        "actionable_suggestions": doc.get("actionable_suggestions", []),
        "score_reason": doc.get("score_reason", ""),
        "brutal_truth": doc.get("brutal_truth", {}),
        "user_questions": doc.get("user_questions", []),
        "differentiation_angles": doc.get("differentiation_angles", []),
        "similar_failures": doc.get("similar_failures", []),
        "pivot_suggestions": doc.get("pivot_suggestions", []),
        "created_at": doc.get("created_at", ""),
    }


@app.get("/api/result/{result_id}")
async def get_result(result_id: str):
    doc = results_collection.find_one({"result_id": result_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Result not found.")
    return serialize_doc(doc)


@app.get("/api/leaderboard")
async def get_leaderboard():
    docs = list(
        results_collection.find(
            {},
            {"_id": 0, "result_id": 1, "idea": 1, "signal": 1, "score": 1, "signal_reason": 1, "verdict": 1, "created_at": 1}
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
            "verdict": doc.get("verdict", ""),
        })
    return {"leaderboard": leaderboard}
