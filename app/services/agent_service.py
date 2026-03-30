from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


def create_agent(db: Session, data: AgentCreate, owner_id: int) -> Agent:
    agent = Agent(**data.model_dump(), owner_id=owner_id)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def get_agents(db: Session, owner_id: int) -> list[Agent]:
    return db.query(Agent).filter(Agent.owner_id == owner_id).all()


def get_agent_or_404(db: Session, agent_id: int, owner_id: int) -> Agent:
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.owner_id == owner_id)
        .first()
    )
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


def update_agent(db: Session, agent_id: int, data: AgentUpdate, owner_id: int) -> Agent:
    agent = get_agent_or_404(db, agent_id, owner_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: int, owner_id: int) -> None:
    agent = get_agent_or_404(db, agent_id, owner_id)
    db.delete(agent)
    db.commit()