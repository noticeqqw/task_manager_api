from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps_auth import get_current_user
from app.db.deps import get_db
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamRead, TeamMemberRead, TeamMemberUpdate

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=TeamRead)
def create_team(
    data: TeamCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Создать команду. Создатель становится владельцем (admin)."""
    existing = db.query(Team).filter(Team.name == data.name).first()
    if existing:
        raise HTTPException(400, "Команда с таким именем уже существует")
    
    team = Team(name=data.name, owner_id=user.id)
    db.add(team)
    
    # Создатель становится участником и админом команды
    user.team_id = team.id
    user.role = "admin"
    
    db.commit()
    db.refresh(team)
    return team


@router.get("/", response_model=list[TeamRead])
def list_all_teams(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Список всех команд"""
    return db.query(Team).all()


@router.get("/my", response_model=list[TeamRead])
def list_my_teams(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Мои команды (где я участник или владелец)"""
    teams = []
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        if team:
            teams.append(team)
    # Также команды, где пользователь владелец
    owned = db.query(Team).filter(Team.owner_id == user.id).all()
    for t in owned:
        if t not in teams:
            teams.append(t)
    return teams


@router.get("/{team_id}", response_model=TeamRead)
def get_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Получить информацию о команде"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Команда не найдена")
    return team


@router.get("/{team_id}/members", response_model=list[TeamMemberRead])
def get_team_members(
    team_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Получить участников команды"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Команда не найдена")
    
    members = db.query(User).filter(User.team_id == team_id).all()
    return [TeamMemberRead(id=m.id, email=str(m.email), role=str(m.role)) for m in members]


@router.post("/{team_id}/join")
def join_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Присоединиться к команде"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Команда не найдена")
    
    if user.team_id:
        raise HTTPException(400, "Вы уже состоите в команде. Сначала выйдите из неё.")
    
    user.team_id = team.id
    user.role = "user"  # Новые участники - обычные пользователи
    db.commit()
    
    return {"detail": "Вы присоединились к команде"}


@router.post("/{team_id}/leave")
def leave_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Покинуть команду"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Команда не найдена")
    
    if user.team_id != team.id:
        raise HTTPException(400, "Вы не состоите в этой команде")
    
    if team.owner_id == user.id:
        raise HTTPException(400, "Владелец не может покинуть команду. Удалите её или передайте владение.")
    
    user.team_id = None
    user.role = "user"
    db.commit()
    
    return {"detail": "Вы покинули команду"}


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberRead)
def update_member_role(
    team_id: UUID,
    user_id: UUID,
    data: TeamMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Изменить роль участника (только владелец или менеджер)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Команда не найдена")
    
    # Проверка прав
    is_owner = team.owner_id == current_user.id
    is_manager = current_user.team_id == team.id and str(current_user.role) == "manager"
    
    if not is_owner and not is_manager:
        raise HTTPException(403, "Нет прав для изменения ролей")
    
    target_user = db.query(User).filter(User.id == user_id, User.team_id == team_id).first()
    if not target_user:
        raise HTTPException(404, "Пользователь не найден в команде")
    
    # Нельзя менять роль владельца
    if team.owner_id == user_id:
        raise HTTPException(400, "Нельзя изменить роль владельца")
    
    # Менеджер не может назначать админов
    if is_manager and data.role == "admin":
        raise HTTPException(403, "Менеджер не может назначать админов")
    
    if data.role not in ["user", "manager", "admin"]:
        raise HTTPException(400, "Недопустимая роль")
    
    target_user.role = data.role
    db.commit()
    db.refresh(target_user)
    
    return TeamMemberRead(id=target_user.id, email=str(target_user.email), role=str(target_user.role))


@router.delete("/{team_id}/members/{user_id}")
def remove_member(
    team_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить участника из команды (только владелец или менеджер)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Команда не найдена")
    
    is_owner = team.owner_id == current_user.id
    is_manager = current_user.team_id == team.id and str(current_user.role) == "manager"
    
    if not is_owner and not is_manager:
        raise HTTPException(403, "Нет прав для удаления участников")
    
    target_user = db.query(User).filter(User.id == user_id, User.team_id == team_id).first()
    if not target_user:
        raise HTTPException(404, "Пользователь не найден в команде")
    
    if team.owner_id == user_id:
        raise HTTPException(400, "Нельзя удалить владельца из команды")
    
    # Менеджер не может удалить другого менеджера или админа
    if is_manager and str(target_user.role) in ["manager", "admin"]:
        raise HTTPException(403, "Менеджер не может удалить другого менеджера или админа")
    
    target_user.team_id = None
    target_user.role = "user"
    db.commit()
    
    return {"detail": "Участник удалён из команды"}


@router.delete("/{team_id}")
def delete_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Удалить команду (только владелец)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Команда не найдена")
    
    if team.owner_id != user.id:
        raise HTTPException(403, "Только владелец может удалить команду")
    
    # Удаляем всех участников из команды
    members = db.query(User).filter(User.team_id == team_id).all()
    for member in members:
        member.team_id = None
        member.role = "user"
    
    db.delete(team)
    db.commit()
    
    return {"detail": "Команда удалена"}
