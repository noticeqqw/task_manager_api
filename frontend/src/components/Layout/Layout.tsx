import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types';
import './Layout.css';

export default function Layout() {
  const { user, logout } = useAuth();

  const getInitials = (email: string) => {
    return email.charAt(0).toUpperCase();
  };

  const getRoleLabel = (role: UserRole) => {
    const roles: Record<UserRole, string> = {
      admin: '👑 Владелец',
      manager: '📋 Менеджер',
      user: '👤 Участник',
    };
    return roles[role] || role;
  };

  const getRoleBadgeClass = (role: UserRole) => {
    return `user-role role-${role}`;
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-left">
          <div className="header-brand">
            <span className="logo">📋</span>
            <h1>Task Manager</h1>
          </div>
          
          <nav className="header-nav">
            <NavLink 
              to="/tasks" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              📝 Задачи
            </NavLink>
            <NavLink 
              to="/teams" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              🏢 Команды
            </NavLink>
          </nav>
        </div>
        
        {user && (
          <div className="header-user">
            <div className="user-info">
              <div className="user-avatar">{getInitials(user.email)}</div>
              <div className="user-details">
                <div className="user-email">{user.email}</div>
                <span className={getRoleBadgeClass(user.role)}>{getRoleLabel(user.role)}</span>
              </div>
            </div>
            <button className="btn-logout" onClick={logout}>
              Выйти
            </button>
          </div>
        )}
      </header>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
