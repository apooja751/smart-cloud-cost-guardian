import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (updated: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('sccg_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('sccg_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const res = await api.get('/auth/me');
          if (res.data.success) {
            setUser(res.data.data);
            localStorage.setItem('sccg_user', JSON.stringify(res.data.data));
          }
        } catch (err) {
          localStorage.removeItem('sccg_token');
          localStorage.removeItem('sccg_user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    if (res.data.success) {
      const { access_token, user: userData } = res.data.data;
      localStorage.setItem('sccg_token', access_token);
      localStorage.setItem('sccg_user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    const res = await api.post('/auth/register', { name, email, password });
    if (res.data.success) {
      const { access_token, user: userData } = res.data.data;
      localStorage.setItem('sccg_token', access_token);
      localStorage.setItem('sccg_user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
    }
  };

  const logout = () => {
    localStorage.removeItem('sccg_token');
    localStorage.removeItem('sccg_user');
    localStorage.removeItem('sccg_active_account');
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  };

  const updateUser = (updated: Partial<User>) => {
    if (user) {
      const newU = { ...user, ...updated };
      setUser(newU);
      localStorage.setItem('sccg_user', JSON.stringify(newU));
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token && !!user, isLoading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
