"use client";

import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, X, User, Mail, Lock, ArrowRight, Check } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface AuthModalsProps {
  showSignUp: boolean;
  showLogIn: boolean;
  onCloseSignUp: () => void;
  onCloseLogIn: () => void;
  onSwitchToLogIn: () => void;
  onSwitchToSignUp: () => void;
}

const AuthModals: React.FC<AuthModalsProps> = ({
  showSignUp,
  showLogIn,
  onCloseSignUp,
  onCloseLogIn,
  onSwitchToLogIn,
  onSwitchToSignUp
}) => {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Reset all states when modal opens/closes
  useEffect(() => {
    if (!showSignUp && !showLogIn) {
      setSignUpData({ name: '', email: '', password: '', confirmPassword: '' });
      setLogInData({ email: '', password: '' });
      setShowPassword(false);
      setShowConfirmPassword(false);
      setIsSubmitted(false);
      setErrorMessage('');
    }
  }, [showSignUp, showLogIn]);

  const [signUpData, setSignUpData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [logInData, setLogInData] = useState({
    email: '',
    password: ''
  });

  const handleSignUpChange = (field: string, value: string) => {
    setSignUpData(prev => ({ ...prev, [field]: value }));
    setErrorMessage('');
  };

  const handleLogInChange = (field: string, value: string) => {
    setLogInData(prev => ({ ...prev, [field]: value }));
    setErrorMessage('');
  };

  const closeModal = (modalType: 'signup' | 'login') => {
    if (modalType === 'signup') {
      onCloseSignUp();
    } else {
      onCloseLogIn();
    }
    setShowPassword(false);
    setShowConfirmPassword(false);
    setIsSubmitted(false);
    setErrorMessage('');
  };

  const handleSignUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (signUpData.password !== signUpData.confirmPassword) {
      setErrorMessage("Passwords do not match!");
      return;
    }

    if (signUpData.password.length < 6) {
      setErrorMessage("Password must be at least 6 characters");
      return;
    }

    setIsSubmitted(true);
    setErrorMessage('');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: signUpData.name,
          email: signUpData.email,
          password: signUpData.password
        }),
      });

      const data = await response.json();

      if (response.ok) {
        login(data.token);
        setSignUpData({ name: '', email: '', password: '', confirmPassword: '' });
        closeModal('signup');
      } else {
        setErrorMessage(data.detail || data.message || "Registration failed");
      }
    } catch (err) {
      console.error("Signup error:", err);
      setErrorMessage("Network error. Please try again.");
    } finally {
      setIsSubmitted(false);
    }
  };

  const handleLogInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitted(true);
    setErrorMessage('');

    try {
      console.log('📤 Sending login request for:', logInData.email);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logInData),
      });

      const data = await response.json();
      console.log('📥 Login response:', data);

      if (response.ok) {
        if (!data.token) {
          console.error('❌ No token in response!', data);
          setErrorMessage("Server didn't return a token");
        } else {
          console.log('✅ Token received, saving to localStorage...');
          login(data.token);
          setLogInData({ email: '', password: '' });
          closeModal('login');
        }
      } else if (response.status === 401) {
        setErrorMessage("Invalid email or password. Please try again.");
      } else {
        setErrorMessage(data.detail || data.message || "Login failed");
      }
    } catch (err) {
      console.error("❌ Login error:", err);
      setErrorMessage("Network error. Please try again.");
    } finally {
      setIsSubmitted(false);
    }
  };

  if (!showSignUp && !showLogIn) return null;

  return (
    <>
      {/* Floating particles background */}
      <div className="fixed inset-0 pointer-events-none z-40">
        {[...Array(15)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-blue-400 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      {/* Sign Up Modal */}
      {showSignUp && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
          <div className="bg-slate-800/40 backdrop-blur-lg border border-blue-500/20 rounded-2xl p-8 shadow-2xl shadow-blue-500/10 w-full max-w-md transform transition-all duration-300 animate-in slide-in-from-bottom-4">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Create Account</h2>
                <p className="text-slate-400">Join us and start your journey</p>
              </div>
              <button
                onClick={() => closeModal('signup')}
                className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors duration-200 group"
              >
                <X size={20} className="text-slate-400 group-hover:text-white" />
              </button>
            </div>

            {errorMessage && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400 text-sm text-center">{errorMessage}</p>
              </div>
            )}

            <form onSubmit={handleSignUpSubmit} className="space-y-6">
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <User size={18} className="text-slate-500 group-focus-within:text-blue-400 transition-colors duration-200" />
                </div>
                <input
                  type="text"
                  value={signUpData.name}
                  onChange={(e) => handleSignUpChange('name', e.target.value)}
                  placeholder="Full Name"
                  className="w-full pl-12 pr-4 py-4 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                  required
                />
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail size={18} className="text-slate-500 group-focus-within:text-blue-400 transition-colors duration-200" />
                </div>
                <input
                  type="email"
                  value={signUpData.email}
                  onChange={(e) => handleSignUpChange('email', e.target.value)}
                  placeholder="Email Address"
                  className="w-full pl-12 pr-4 py-4 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                  required
                />
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock size={18} className="text-slate-500 group-focus-within:text-blue-400 transition-colors duration-200" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={signUpData.password}
                  onChange={(e) => handleSignUpChange('password', e.target.value)}
                  placeholder="Password"
                  className="w-full pl-12 pr-12 py-4 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center hover:bg-slate-700/30 rounded-r-xl transition-colors duration-200"
                >
                  {showPassword ? <EyeOff size={18} className="text-slate-500" /> : <Eye size={18} className="text-slate-500" />}
                </button>
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock size={18} className="text-slate-500 group-focus-within:text-blue-400 transition-colors duration-200" />
                </div>
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={signUpData.confirmPassword}
                  onChange={(e) => handleSignUpChange('confirmPassword', e.target.value)}
                  placeholder="Confirm Password"
                  className="w-full pl-12 pr-12 py-4 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center hover:bg-slate-700/30 rounded-r-xl"
                >
                  {showConfirmPassword ? <EyeOff size={18} className="text-slate-500" /> : <Eye size={18} className="text-slate-500" />}
                </button>
              </div>

              <button
                type="submit"
                disabled={isSubmitted}
                className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-4 px-8 rounded-xl font-semibold text-lg flex items-center justify-center space-x-3 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25 hover:scale-[1.02] disabled:opacity-50"
              >
                <span>{isSubmitted ? 'Creating Account...' : 'Create Account'}</span>
                {isSubmitted ? <Check size={20} className="animate-bounce" /> : <ArrowRight size={20} />}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-slate-400">
                Already have an account?{' '}
                <button onClick={onSwitchToLogIn} className="text-blue-400 hover:text-blue-300 font-semibold">
                  Sign In
                </button>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Log In Modal */}
      {showLogIn && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
          <div className="bg-slate-800/40 backdrop-blur-lg border border-cyan-500/20 rounded-2xl p-8 shadow-2xl shadow-cyan-500/10 w-full max-w-md transform transition-all duration-300 animate-in slide-in-from-bottom-4">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Welcome Back</h2>
                <p className="text-slate-400">Sign in to your account</p>
              </div>
              <button
                onClick={() => closeModal('login')}
                className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors duration-200 group"
              >
                <X size={20} className="text-slate-400 group-hover:text-white" />
              </button>
            </div>

            {errorMessage && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400 text-sm text-center">{errorMessage}</p>
              </div>
            )}

            <form onSubmit={handleLogInSubmit} className="space-y-6">
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail size={18} className="text-slate-500 group-focus-within:text-cyan-400 transition-colors duration-200" />
                </div>
                <input
                  type="email"
                  value={logInData.email}
                  onChange={(e) => handleLogInChange('email', e.target.value)}
                  placeholder="Email Address"
                  className="w-full pl-12 pr-4 py-4 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all duration-300"
                  required
                />
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock size={18} className="text-slate-500 group-focus-within:text-cyan-400 transition-colors duration-200" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={logInData.password}
                  onChange={(e) => handleLogInChange('password', e.target.value)}
                  placeholder="Password"
                  className="w-full pl-12 pr-12 py-4 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all duration-300"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center hover:bg-slate-700/30 rounded-r-xl"
                >
                  {showPassword ? <EyeOff size={18} className="text-slate-500" /> : <Eye size={18} className="text-slate-500" />}
                </button>
              </div>

              <button
                type="submit"
                disabled={isSubmitted}
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-4 px-8 rounded-xl font-semibold text-lg flex items-center justify-center space-x-3 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25 hover:scale-[1.02] disabled:opacity-50"
              >
                <span>{isSubmitted ? 'Signing In...' : 'Sign In'}</span>
                {isSubmitted ? <Check size={20} className="animate-bounce" /> : <ArrowRight size={20} />}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-slate-400">
                Don't have an account?{' '}
                <button onClick={onSwitchToSignUp} className="text-cyan-400 hover:text-cyan-300 font-semibold">
                  Sign Up
                </button>
              </p>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .animate-in { animation: fadeIn 0.3s ease-out; }
        .fade-in { animation: fadeIn 0.3s ease-out; }
        .slide-in-from-bottom-4 { animation: slideInFromBottom 0.3s ease-out; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideInFromBottom {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  );
};

export default AuthModals;
