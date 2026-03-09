import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient

from planner_agent.core.planner_agent import PlannerAgent


MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
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


app = FastAPI(title="Planning Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
        raise HTTPException(status_code=400, detail="projectDescription is required")

    # Use existing PlannerAgent for plan logic
    agent = PlannerAgent()

    try:
        # Here we tie the free-text description into a fixed goal
        goal = "BUILDING A MALL"
        schedule = agent.plan("CONTRACTOR", goal)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))

    # Map schedule into the shape expected by the frontend
    phases = [f"Day {item['day']}: {item['task_name']}" for item in schedule]

    plan_response = {
        "phases": phases,
        "resources": [
            "Resources are validated via ResourceValidator in the planner engine.",
        ],
        "timeline": f"Total Days: {len(schedule)}",
        "risks": [
            "Resource shortages may reorder tasks.",
            "LLM task decomposition quality affects schedule detail.",
        ],
        "cost": "Cost estimation can be layered on top of tasks (not implemented yet).",
    }

    plans_collection.insert_one(
        {
            "description": description,
            "created_at": datetime.utcnow(),
            "plan": plan_response,
        }
    )

    return plan_response

