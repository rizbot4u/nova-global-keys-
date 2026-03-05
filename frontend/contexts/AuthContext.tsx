"use client";
import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  isAuthenticated: boolean;
  session: string | null;
  login: (token: string) => void;
  logout: () => void;
  returnPath: string | null;
  setReturnPath: (path: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<string | null>(null);
  const [returnPath, setReturnPath] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('nova_session');
    setSession(token);
    setIsReady(true);
  }, []);

  const login = (token: string) => {
    localStorage.setItem('nova_session', token);
    setSession(token);
    
    // Redirect to return path if exists
    if (returnPath) {
      router.push(returnPath);
      setReturnPath(null);
    }
  };

  const logout = () => {
    localStorage.removeItem('nova_session');
    setSession(null);
    router.push('/');
  };

  if (!isReady) return null;

  return (
    <AuthContext.Provider value={{
      isAuthenticated: !!session,
      session,
      login,
      logout,
      returnPath,
      setReturnPath
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
