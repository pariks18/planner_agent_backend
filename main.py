import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from core.planner_agent import PlannerAgent


load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "planning_agent")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]
users_collection = db["users"]
plans_collection = db["plans"]


class AuthRequest(BaseModel):
    role: str
    password: str


class PlanRequest(BaseModel):
    projectDescription: str
    role: str | None = None


app = FastAPI(title="Planning Agent API")

cors_origins_from_env = [
    origin.strip()
    for origin in (os.getenv("CORS_ORIGINS") or "").split(",")
    if origin.strip()
]
cors_origin_regex = (os.getenv("CORS_ORIGIN_REGEX") or "").strip() or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        *cors_origins_from_env,
    ],
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_demo_users():
    """Seed a few demo users if collection is empty."""
    if users_collection.count_documents({}) == 0:
        demo_password = "admin123"
        demo_roles = [
            "Site Manager",
            "Project Engineer",
            "Construction Manager",
            "Contractor",
            "Architect",
            "Quantity Surveyor",
        ]
        users_collection.insert_many(
            {"role": role, "password": demo_password}
            for role in demo_roles
        )


@app.on_event("startup")
def on_startup():
    ensure_demo_users()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/auth/verify")
def verify_auth(payload: AuthRequest):
    user = users_collection.find_one(
        {"role": payload.role, "password": payload.password}
    )
    return {"authorized": bool(user)}


@app.post("/api/plan")
def generate_plan(payload: PlanRequest):
    description = payload.projectDescription.strip()
    if not description:
        return {"error": "projectDescription is required"}

    # Use PlannerAgent (LLM-backed) to generate tasks/schedule
    agent = PlannerAgent()

    try:
        role_label = (payload.role or "").strip()
        role_map = {
            "Site Manager": "SITE_MANAGER",
            "Project Engineer": "PROJECT_ENGINEER",
            "Construction Manager": "CONSTRUCTION_MANAGER",
            "Contractor": "CONTRACTOR",
            "Architect": "ARCHITECT",
            "Quantity Surveyor": "QUANTITY_SURVEYOR",
        }
        role_code = role_map.get(role_label, "CONTRACTOR")

        # IMPORTANT: pass the user's input to the LLM as the goal
        schedule = agent.plan(role_code, description)
    except Exception as exc:  # noqa: BLE001
        # Always return a JSON error payload rather than HTTP 500/403
        return {"error": f"Planner failed to generate schedule: {exc}"}

    plan_response = {
        "schedule": schedule,  # list of {task_id, task_name, day}
    }

    plans_collection.insert_one(
        {
            "description": description,
            "created_at": datetime.utcnow(),
            "plan": plan_response,
        }
    )

    return plan_response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

