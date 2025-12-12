import { useState, useEffect } from 'react';
import type { Team, TeamCreate, TeamMember } from '../../types';
import { teamsApi } from '../../api';
import { useAuth } from '../../context/AuthContext';
import './Teams.css';

export default function TeamsPage() {
  const { user } = useAuth();
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await teamsApi.getAll();
      setTeams(data);
    } catch (err) {
      setError('Ошибка загрузки команд');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMembers = async (teamId: string) => {
    try {
      const data = await teamsApi.getMembers(teamId);
      setMembers(data);
    } catch (err) {
      console.error('Error loading members:', err);
    }
  };

  const handleSelectTeam = async (team: Team) => {
    setSelectedTeam(team);
    await loadMembers(team.id);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTeamName.trim()) return;

    try {
      const data: TeamCreate = { name: newTeamName.trim() };
      const newTeam = await teamsApi.create(data);
      setTeams([...teams, newTeam]);
      setNewTeamName('');
      setIsCreating(false);
      // Обновляем страницу чтобы получить новую роль
      window.location.reload();
    } catch (err: any) {
      console.error('Error creating team:', err);
      setError(err.response?.data?.detail || 'Ошибка создания команды');
    }
  };

  const handleJoin = async (teamId: string) => {
    try {
      await teamsApi.join(teamId);
      window.location.reload();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка присоединения');
    }
  };

  const handleLeave = async (teamId: string) => {
    if (!confirm('Вы уверены, что хотите покинуть команду?')) return;
    try {
      await teamsApi.leave(teamId);
      window.location.reload();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка выхода из команды');
    }
  };

  const handleDelete = async (teamId: string) => {
    if (!confirm('Вы уверены? Все участники будут удалены из команды.')) return;
    try {
      await teamsApi.delete(teamId);
      setTeams(teams.filter(t => t.id !== teamId));
      setSelectedTeam(null);
      window.location.reload();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления команды');
    }
  };

  const handleUpdateRole = async (userId: string, role: string) => {
    if (!selectedTeam) return;
    try {
      await teamsApi.updateMemberRole(selectedTeam.id, userId, role);
      await loadMembers(selectedTeam.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка изменения роли');
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!selectedTeam) return;
    if (!confirm('Удалить участника из команды?')) return;
    try {
      await teamsApi.removeMember(selectedTeam.id, userId);
      await loadMembers(selectedTeam.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления участника');
    }
  };

  const isOwner = (team: Team) => team.owner_id === user?.id;
  const isMember = (team: Team) => user?.team_id === team.id;
  const canManage = selectedTeam && (isOwner(selectedTeam) || (isMember(selectedTeam) && user?.role === 'manager'));

  if (isLoading) {
    return <div className="teams-loading">Загрузка команд...</div>;
  }

  return (
    <div className="teams-page">
      <div className="teams-header">
        <div>
          <h1>🏢 Команды</h1>
          <p className="teams-subtitle">
            {user?.team_id 
              ? `Вы состоите в команде • Роль: ${user.role === 'admin' ? 'Владелец' : user.role === 'manager' ? 'Менеджер' : 'Участник'}`
              : 'Создайте команду или присоединитесь к существующей'}
          </p>
        </div>
        {!user?.team_id && (
          <button 
            className="btn-create-team"
            onClick={() => setIsCreating(true)}
          >
            ➕ Создать команду
          </button>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {isCreating && (
        <div className="create-team-form">
          <h3>Новая команда</h3>
          <form onSubmit={handleCreate}>
            <input
              type="text"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Название команды"
              autoFocus
            />
            <div className="form-actions">
              <button type="submit" className="btn-save">✓ Создать</button>
              <button 
                type="button" 
                className="btn-cancel"
                onClick={() => { setIsCreating(false); setNewTeamName(''); }}
              >
                ✗ Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="teams-content">
        <div className="teams-list">
          <h2>Все команды</h2>
          {teams.length === 0 ? (
            <div className="teams-empty">
              <p>🏢 Команды пока не созданы</p>
            </div>
          ) : (
            teams.map(team => (
              <div 
                key={team.id} 
                className={`team-item ${selectedTeam?.id === team.id ? 'selected' : ''} ${isMember(team) ? 'my-team' : ''}`}
                onClick={() => handleSelectTeam(team)}
              >
                <div className="team-item-info">
                  <span className="team-name">{team.name}</span>
                  {isOwner(team) && <span className="owner-badge">👑 Вы владелец</span>}
                  {isMember(team) && !isOwner(team) && <span className="member-badge">✓ Ваша команда</span>}
                </div>
                <div className="team-item-actions">
                  {!user?.team_id && (
                    <button 
                      className="btn-join"
                      onClick={(e) => { e.stopPropagation(); handleJoin(team.id); }}
                    >
                      Вступить
                    </button>
                  )}
                  {isMember(team) && !isOwner(team) && (
                    <button 
                      className="btn-leave"
                      onClick={(e) => { e.stopPropagation(); handleLeave(team.id); }}
                    >
                      Выйти
                    </button>
                  )}
                  {isOwner(team) && (
                    <button 
                      className="btn-delete"
                      onClick={(e) => { e.stopPropagation(); handleDelete(team.id); }}
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {selectedTeam && (
          <div className="team-details">
            <h2>👥 Участники: {selectedTeam.name}</h2>
            {members.length === 0 ? (
              <p className="no-members">В команде пока нет участников</p>
            ) : (
              <div className="members-list">
                {members.map(member => (
                  <div key={member.id} className="member-item">
                    <div className="member-info">
                      <div className="member-avatar">{member.email.charAt(0).toUpperCase()}</div>
                      <div className="member-details">
                        <span className="member-email">{member.email}</span>
                        <span className={`member-role role-${member.role}`}>
                          {member.role === 'admin' ? '👑 Владелец' : member.role === 'manager' ? '📋 Менеджер' : '👤 Участник'}
                        </span>
                      </div>
                    </div>
                    {canManage && member.id !== selectedTeam.owner_id && member.id !== user?.id && (
                      <div className="member-actions">
                        <select 
                          value={member.role}
                          onChange={(e) => handleUpdateRole(member.id, e.target.value)}
                          className="role-select"
                        >
                          <option value="user">Участник</option>
                          <option value="manager">Менеджер</option>
                          {isOwner(selectedTeam) && <option value="admin">Админ</option>}
                        </select>
                        <button 
                          className="btn-remove-member"
                          onClick={() => handleRemoveMember(member.id)}
                        >
                          ✗
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="roles-info">
        <h3>📖 Роли в команде</h3>
        <div className="roles-grid">
          <div className="role-card">
            <span className="role-icon">👑</span>
            <h4>Владелец (Admin)</h4>
            <p>Создатель команды. Может управлять участниками, назначать роли и удалять команду.</p>
          </div>
          <div className="role-card">
            <span className="role-icon">📋</span>
            <h4>Менеджер</h4>
            <p>Может создавать задачи, назначать исполнителей и управлять обычными участниками.</p>
          </div>
          <div className="role-card">
            <span className="role-icon">👤</span>
            <h4>Участник</h4>
            <p>Может просматривать задачи и выполнять назначенные ему задачи.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
