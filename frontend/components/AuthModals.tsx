"use client";

import React, { useState } from 'react';
import { Eye, EyeOff, X, User, Mail, Lock, ArrowRight, Check } from 'lucide-react';

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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

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
    setSignUpData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLogInChange = (field: string, value: string) => {
    setLogInData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSignUpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitted(true);
    console.log('Sign up data:', signUpData);
    setTimeout(() => {
      setIsSubmitted(false);
      onCloseSignUp();
      setSignUpData({ name: '', email: '', password: '', confirmPassword: '' });
    }, 2000);
  };

  const handleLogInSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitted(true);
    console.log('Log in data:', logInData);
    setTimeout(() => {
      setIsSubmitted(false);
      onCloseLogIn();
      setLogInData({ email: '', password: '' });
    }, 2000);
  };

  const closeModal = (modalType: 'signup' | 'login') => {
    if (modalType === 'signup') {
      onCloseSignUp();
    } else {
      onCloseLogIn();
    }
    setIsSubmitted(false);
    setShowPassword(false);
    setShowConfirmPassword(false);
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
            {/* Header */}
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

            <form onSubmit={handleSignUpSubmit} className="space-y-6">
              {/* Name Field */}
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
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100 transition-opacity duration-300" />
              </div>

              {/* Email Field */}
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
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100 transition-opacity duration-300" />
              </div>

              {/* Password Field */}
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
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center hover:bg-slate-700/30 rounded-r-xl transition-colors duration-200"
                >
                  {showPassword ? (
                    <EyeOff size={18} className="text-slate-500 hover:text-blue-400" />
                  ) : (
                    <Eye size={18} className="text-slate-500 hover:text-blue-400" />
                  )}
                </button>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100 transition-opacity duration-300" />
              </div>

              {/* Confirm Password Field */}
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
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center hover:bg-slate-700/30 rounded-r-xl transition-colors duration-200"
                >
                  {showConfirmPassword ? (
                    <EyeOff size={18} className="text-slate-500 hover:text-blue-400" />
                  ) : (
                    <Eye size={18} className="text-slate-500 hover:text-blue-400" />
                  )}
                </button>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100 transition-opacity duration-300" />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitted}
                className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-4 px-8 rounded-xl font-semibold text-lg flex items-center justify-center space-x-3 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>{isSubmitted ? 'Account Created!' : 'Create Account'}</span>
                {isSubmitted ? (
                  <Check size={20} className="animate-bounce" />
                ) : (
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-200" />
                )}
              </button>
            </form>

            {/* Footer */}
            <div className="mt-6 text-center">
              <p className="text-slate-400">
                Already have an account?{' '}
                <button
                  onClick={onSwitchToLogIn}
                  className="text-blue-400 hover:text-blue-300 font-semibold transition-colors duration-200"
                >
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
            {/* Header */}
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

            <form onSubmit={handleLogInSubmit} className="space-y-6">
              {/* Email Field */}
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
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/5 to-blue-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100 transition-opacity duration-300" />
              </div>

              {/* Password Field */}
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
                  className="absolute inset-y-0 right-0 pr-4 flex items-center hover:bg-slate-700/30 rounded-r-xl transition-colors duration-200"
                >
                  {showPassword ? (
                    <EyeOff size={18} className="text-slate-500 hover:text-cyan-400" />
                  ) : (
                    <Eye size={18} className="text-slate-500 hover:text-cyan-400" />
                  )}
                </button>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/5 to-blue-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100 transition-opacity duration-300" />
              </div>

              {/* Forgot Password */}
              <div className="text-right">
                <button
                  type="button"
                  className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors duration-200"
                >
                  Forgot Password?
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitted}
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-4 px-8 rounded-xl font-semibold text-lg flex items-center justify-center space-x-3 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>{isSubmitted ? 'Welcome Back!' : 'Sign In'}</span>
                {isSubmitted ? (
                  <Check size={20} className="animate-bounce" />
                ) : (
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-200" />
                )}
              </button>
            </form>

            {/* Footer */}
            <div className="mt-6 text-center">
              <p className="text-slate-400">
                Don't have an account?{' '}
                <button
                  onClick={onSwitchToSignUp}
                  className="text-cyan-400 hover:text-cyan-300 font-semibold transition-colors duration-200"
                >
                  Sign Up
                </button>
              </p>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .animate-in {
          animation: fadeIn 0.3s ease-out;
        }
        
        .fade-in {
          animation: fadeIn 0.3s ease-out;
        }
        
        .slide-in-from-bottom-4 {
          animation: slideInFromBottom 0.3s ease-out;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes slideInFromBottom {
          from { 
            opacity: 0;
            transform: translateY(16px);
          }
          to { 
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  );
};

export default AuthModals;