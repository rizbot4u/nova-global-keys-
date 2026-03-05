"use client";

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import AuthModals from '../components/AuthModals';

const Navbar = () => {
  const pathname = usePathname();
  const router = useRouter();
  const [hoveredLink, setHoveredLink] = useState('');
  const [showSignUp, setShowSignUp] = useState(false);
  const [showLogIn, setShowLogIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // NEW: Auth State
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check for session on load
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('nova_session');
      setIsLoggedIn(!!token);
    };
    
    checkAuth();
    // Watch for login/logout events in other tabs
    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, []);

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Trading Bots', href: '/trading-bots' },
    { name: 'Price Charts', href: '/price-charts' },
    { name: 'Plans', href: '/plans' },
    // Only show Terminal link if logged in
    ...(isLoggedIn ? [{ name: 'Terminal', href: '/dashboard' }] : []),
    { name: 'About Us', href: '/about-us' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('nova_session');
    setIsLoggedIn(false);
    router.push('/');
    router.refresh();
  };

  const isActiveLink = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  const handleSignUpClick = () => { setShowSignUp(true); setShowLogIn(false); setIsMobileMenuOpen(false); };
  const handleLogInClick = () => { setShowLogIn(true); setShowSignUp(false); setIsMobileMenuOpen(false); };
  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  return (
    <>
      <nav className="relative bg-gradient-to-br from-slate-900 to-slate-800 border-b border-blue-500/10 overflow-hidden">
        {/* Animated background patterns (Kept from your original) */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 0.3, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="absolute inset-0"
          style={{
            backgroundImage: `radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.15) 1px, transparent 1px), radial-gradient(circle at 80% 30%, rgba(34, 197, 94, 0.1) 1px, transparent 1px)`,
            backgroundSize: '50px 50px, 80px 80px'
          }}
        />
        
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-3 sm:py-2"
        >
          <div className="flex items-center justify-between">
            {/* Logo */}
            <motion.div initial={{ x: -30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="flex items-center">
              <Link href="/">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Image src="/images/logo.svg" alt="Nova Logo" width={48} height={48} className="w-10 h-10 md:w-12 md:h-12" priority />
                </motion.div>
              </Link>
            </motion.div>

            {/* Desktop Nav */}
            <ul className="hidden lg:flex items-center space-x-8 xl:space-x-10">
              {navLinks.map((link, index) => {
                const isActive = isActiveLink(link.href);
                return (
                  <motion.li key={link.name} initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 + index * 0.05 }}>
                    <Link href={link.href}>
                      <span 
                        className={`relative font-medium py-2 text-sm transition-colors cursor-pointer ${isActive ? 'text-blue-400' : 'text-slate-300 hover:text-blue-400'}`}
                        onMouseEnter={() => setHoveredLink(link.name)}
                        onMouseLeave={() => setHoveredLink('')}
                      >
                        {link.name}
                        {isActive && (
                          <motion.div layoutId="activeUnderline" className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500" />
                        )}
                      </span>
                    </Link>
                  </motion.li>
                );
              })}
            </ul>
            
            {/* Action Buttons: Toggles based on Login State */}
            <motion.div initial={{ x: 50, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="hidden sm:flex items-center space-x-3">
              {isLoggedIn ? (
                <>
                  <Link href="/dashboard">
                    <motion.button 
                      whileHover={{ scale: 1.03 }}
                      className="bg-blue-600/20 border border-blue-500/50 text-blue-400 font-bold px-4 py-2 rounded-lg text-sm uppercase tracking-tighter"
                    >
                      Open Terminal
                    </motion.button>
                  </Link>
                  <button 
                    onClick={handleLogout}
                    className="text-slate-400 hover:text-red-400 font-bold text-xs uppercase transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <motion.button 
                    onClick={handleSignUpClick}
                    whileHover={{ scale: 1.03, boxShadow: "0 8px 20px rgba(59, 130, 246, 0.4)" }}
                    className="bg-blue-600 text-white font-semibold px-6 py-2.5 rounded-lg text-sm"
                  >
                    Sign Up
                  </motion.button>
                  <motion.button 
                    onClick={handleLogInClick}
                    whileHover={{ scale: 1.03, backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
                    className="border-2 border-blue-500/30 text-slate-300 font-semibold px-6 py-2 rounded-lg text-sm"
                  >
                    Login
                  </motion.button>
                </>
              )}
            </motion.div>

            {/* Mobile Toggle */}
            <button onClick={toggleMobileMenu} className="lg:hidden p-2 text-slate-300">
               <div className="w-6 h-0.5 bg-current mb-1.5" />
               <div className="w-6 h-0.5 bg-current mb-1.5" />
               <div className="w-6 h-0.5 bg-current" />
            </button>
          </div>
        </motion.div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="lg:hidden bg-slate-900 border-t border-blue-500/20">
              <div className="px-6 py-4 space-y-4">
                {navLinks.map((link) => (
                  <Link key={link.name} href={link.href} onClick={closeMobileMenu} className="block text-slate-300 py-2">
                    {link.name}
                  </Link>
                ))}
                <div className="pt-4 border-t border-slate-800">
                  {isLoggedIn ? (
                    <button onClick={handleLogout} className="w-full text-left text-red-400 font-bold">LOGOUT</button>
                  ) : (
                    <button onClick={handleLogInClick} className="w-full bg-blue-600 py-3 rounded-lg text-white">LOGIN</button>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      <AuthModals
        showSignUp={showSignUp} showLogIn={showLogIn}
        onCloseSignUp={() => setShowSignUp(false)} onCloseLogIn={() => setShowLogIn(false)}
        onSwitchToLogIn={() => { setShowSignUp(false); setShowLogIn(true); }}
        onSwitchToSignUp={() => { setShowLogIn(false); setShowSignUp(true); }}
      />
    </>
  );
};

export default Navbar;
