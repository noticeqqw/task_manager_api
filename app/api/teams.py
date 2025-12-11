from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps_auth import require_admin
from app.db.deps import get_db
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamRead

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=TeamRead)
def create_team(
    data: TeamCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    team = Team(name=data.name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/", response_model=list[TeamRead])
def list_teams(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(Team).all()


@router.delete("/{team_id}")
def delete_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Team not found")

    db.delete(team)
    db.commit()
    return {"detail": "Team deleted"}
