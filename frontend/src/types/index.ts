export type UserRole = 'admin' | 'manager' | 'user';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  team_id?: string | null;
}

export interface Team {
  id: string;
  name: string;
  owner_id: string;
}

export interface TeamCreate {
  name: string;
}

export interface TeamMember {
  id: string;
  email: string;
  role: UserRole;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: 'todo' | 'in_progress' | 'done';
  creator_id: string;
  assignee_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: string;
  assignee_id?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: string;
  assignee_id?: string | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
}
