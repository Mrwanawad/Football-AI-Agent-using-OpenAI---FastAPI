from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from app.services import agent_service

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("", response_model=AgentResponse, status_code=201)
def create_agent(
    data: AgentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new AI agent."""
    return agent_service.create_agent(db, data, owner_id=user_id)


@router.get("", response_model=list[AgentResponse])
def list_agents(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """List all agents owned by the current user."""
    return agent_service.get_agents(db, owner_id=user_id)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Retrieve a single agent by ID."""
    return agent_service.get_agent_or_404(db, agent_id, owner_id=user_id)


@router.patch("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    data: AgentUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Partially update an agent's name or system prompt."""
    return agent_service.update_agent(db, agent_id, data, owner_id=user_id)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete an agent and all its sessions."""
    agent_service.delete_agent(db, agent_id, owner_id=user_id)