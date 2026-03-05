"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { Menu, X, ChevronRight, LogOut, LayoutDashboard } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext'; // Added this
import AuthModals from './AuthModals';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showSignUp, setShowSignUp] = useState(false);
  const [showLogIn, setShowLogIn] = useState(false);
  
  // Consume the global Auth state
  const { isAuthenticated, logout } = useAuth(); 

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Trading Bots', href: '/trading-bots' },
    { name: 'Pricing', href: '/pricing' },
    { name: 'About', href: '/about' },
  ];

  return (
    <nav className="fixed w-full z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">N</span>
              </div>
              <span className="text-white font-bold text-xl tracking-tight">NOVA</span>
            </Link>
          </div>

          {/* Desktop Nav Links */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className="text-slate-300 hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>

          {/* Auth Actions */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              // SHOW THIS WHEN LOGGED IN
              <div className="flex items-center space-x-4">
                <Link 
                  href="/dashboard"
                  className="flex items-center space-x-2 text-slate-300 hover:text-white transition-colors"
                >
                  <LayoutDashboard size={18} />
                  <span>Dashboard</span>
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center space-x-2 bg-slate-800 hover:bg-red-500/20 text-slate-300 hover:text-red-400 px-4 py-2 rounded-xl border border-slate-700 hover:border-red-500/50 transition-all duration-300"
                >
                  <LogOut size={18} />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              // SHOW THIS WHEN LOGGED OUT
              <>
                <button 
                  onClick={() => setShowLogIn(true)}
                  className="text-slate-300 hover:text-white px-4 py-2 text-sm font-medium transition-colors"
                >
                  Sign In
                </button>
                <button 
                  onClick={() => setShowSignUp(true)}
                  className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 shadow-lg shadow-blue-500/20 flex items-center space-x-2"
                >
                  <span>Get Started</span>
                  <ChevronRight size={16} />
                </button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none transition-colors"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-800">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                className="text-slate-300 hover:text-blue-400 block px-3 py-2 rounded-md text-base font-medium"
                onClick={() => setIsOpen(false)}
              >
                {link.name}
              </Link>
            ))}
            {isAuthenticated && (
              <Link
                href="/dashboard"
                className="text-slate-300 hover:text-blue-400 block px-3 py-2 rounded-md text-base font-medium"
                onClick={() => setIsOpen(false)}
              >
                Dashboard
              </Link>
            )}
            <div className="pt-4 pb-3 border-t border-slate-800">
              {isAuthenticated ? (
                <button
                  onClick={() => { logout(); setIsOpen(false); }}
                  className="w-full text-left flex items-center space-x-2 px-3 py-2 text-red-400 font-medium"
                >
                  <LogOut size={18} />
                  <span>Logout</span>
                </button>
              ) : (
                <div className="space-y-2 px-3">
                  <button onClick={() => { setShowLogIn(true); setIsOpen(false); }} className="w-full text-left text-slate-300 py-2">Sign In</button>
                  <button onClick={() => { setShowSignUp(true); setIsOpen(false); }} className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold">Get Started</button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      <AuthModals 
        showSignUp={showSignUp}
        showLogIn={showLogIn}
        onCloseSignUp={() => setShowSignUp(false)}
        onCloseLogIn={() => setShowLogIn(false)}
        onSwitchToLogIn={() => { setShowSignUp(false); setShowLogIn(true); }}
        onSwitchToSignUp={() => { setShowLogIn(false); setShowSignUp(true); }}
      />
    </nav>
  );
};

export default Navbar;
