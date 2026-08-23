import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { AWSAccount } from '../types';
import { useAuth } from './AuthContext';

interface AWSAccountContextType {
  accounts: AWSAccount[];
  activeAccount: AWSAccount | null;
  isLoading: boolean;
  setActiveAccount: (acc: AWSAccount | null) => void;
  refreshAccounts: () => Promise<void>;
  syncAccount: (id: number) => Promise<void>;
  isDemoMode: boolean;
}

const AWSAccountContext = createContext<AWSAccountContextType | undefined>(undefined);

export const AWSAccountProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [accounts, setAccounts] = useState<AWSAccount[]>([]);
  const [activeAccount, setActiveAccountState] = useState<AWSAccount | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const refreshAccounts = async () => {
    if (!isAuthenticated) return;
    setIsLoading(true);
    try {
      const res = await api.get('/aws/accounts');
      if (res.data.success) {
        const accList: AWSAccount[] = res.data.data;
        setAccounts(accList);

        // Restore active account or pick first
        const savedId = localStorage.getItem('sccg_active_account');
        if (savedId) {
          const match = accList.find((a) => a.id === Number(savedId));
          if (match) {
            setActiveAccountState(match);
            return;
          }
        }
        if (accList.length > 0) {
          setActiveAccountState(accList[0]);
          localStorage.setItem('sccg_active_account', String(accList[0].id));
        } else {
          setActiveAccountState(null);
        }
      }
    } catch (err) {
      console.error('Failed to load AWS accounts', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      refreshAccounts();
    } else {
      setAccounts([]);
      setActiveAccountState(null);
    }
  }, [isAuthenticated]);

  const setActiveAccount = (acc: AWSAccount | null) => {
    setActiveAccountState(acc);
    if (acc) {
      localStorage.setItem('sccg_active_account', String(acc.id));
    } else {
      localStorage.removeItem('sccg_active_account');
    }
  };

  const syncAccount = async (id: number) => {
    try {
      await api.post(`/aws/sync/${id}`);
      await refreshAccounts();
    } catch (err) {
      console.error('Sync failed', err);
      throw err;
    }
  };

  const isDemoMode = activeAccount?.connection_type === 'DEMO';

  return (
    <AWSAccountContext.Provider value={{ accounts, activeAccount, isLoading, setActiveAccount, refreshAccounts, syncAccount, isDemoMode }}>
      {children}
    </AWSAccountContext.Provider>
  );
};

export const useAWSAccount = () => {
  const context = useContext(AWSAccountContext);
  if (!context) throw new Error('useAWSAccount must be used within an AWSAccountProvider');
  return context;
};
