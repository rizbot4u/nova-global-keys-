"use client";

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import AuthModals from '../components/AuthModals';

const Navbar = () => {
  const pathname = usePathname();
  const [hoveredLink, setHoveredLink] = useState('');
  const [showSignUp, setShowSignUp] = useState(false);
  const [showLogIn, setShowLogIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Trading Bots', href: '/trading-bots' },
    { name: 'Price Charts', href: '/price-charts' },
    { name: 'Plans', href: '/plans' },
    { name: 'About Us', href: '/about-us' },
    { name: 'Contact Us', href: '/contact-us' }
  ];

  const isActiveLink = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  const handleSignUpClick = () => {
    setShowSignUp(true);
    setShowLogIn(false);
    setIsMobileMenuOpen(false);
  };

  const handleLogInClick = () => {
    setShowLogIn(true);
    setShowSignUp(false);
    setIsMobileMenuOpen(false);
  };

  const handleCloseSignUp = () => {
    setShowSignUp(false);
  };

  const handleCloseLogIn = () => {
    setShowLogIn(false);
  };

  const handleSwitchToLogIn = () => {
    setShowSignUp(false);
    setShowLogIn(true);
  };

  const handleSwitchToSignUp = () => {
    setShowLogIn(false);
    setShowSignUp(true);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <nav 
        className="relative bg-gradient-to-br from-slate-900 to-slate-800 border-b border-blue-500/10 overflow-hidden"
      >
        {/* Background pattern with animation */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 0.3, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="absolute inset-0"
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.15) 1px, transparent 1px),
              radial-gradient(circle at 80% 30%, rgba(34, 197, 94, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 40% 70%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 90% 80%, rgba(34, 197, 94, 0.08) 1px, transparent 1px),
              radial-gradient(circle at 10% 90%, rgba(59, 130, 246, 0.08) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px, 80px 80px, 60px 60px, 90px 90px, 70px 70px'
          }}
        />
        
        {/* Animated gradient overlays */}
        <motion.div 
          animate={{ 
            background: [
              "linear-gradient(45deg, transparent 30%, rgba(59, 130, 246, 0.02) 50%, transparent 70%)",
              "linear-gradient(45deg, transparent 20%, rgba(59, 130, 246, 0.04) 60%, transparent 80%)",
              "linear-gradient(45deg, transparent 30%, rgba(59, 130, 246, 0.02) 50%, transparent 70%)"
            ]
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className="absolute inset-0"
        />
        <motion.div 
          animate={{ 
            background: [
              "linear-gradient(-45deg, transparent 30%, rgba(34, 197, 94, 0.02) 50%, transparent 70%)",
              "linear-gradient(-45deg, transparent 40%, rgba(34, 197, 94, 0.03) 40%, transparent 60%)",
              "linear-gradient(-45deg, transparent 30%, rgba(34, 197, 94, 0.02) 50%, transparent 70%)"
            ]
          }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
          className="absolute inset-0"
        />
        
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-3 sm:py-2"
        >
          <div className="flex items-center justify-between">
            {/* Logo/Brand (Optional - you can add your logo here) */}
            <motion.div 
              initial={{ x: -30, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="flex items-center"
            >
              <Link href="/">
                <motion.span 
                  className="text-white font-bold text-xl sm:text-2xl cursor-pointer"
                  whileHover={{ 
                    scale: 1.05,
                    color: '#3b82f6',
                    transition: { duration: 0.2 }
                  }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Image
                    src="/images/logo.svg"
                    alt="AI Bot Logo"
                    width={48}
                    height={48}
                    className="w-10 h-10 md:w-12 md:h-12 object-contain"
                    priority
                  />
                </motion.span>
              </Link>
            </motion.div>

            {/* Desktop Navigation Links */}
            <motion.ul 
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.15 }}
              className="hidden lg:flex items-center space-x-8 xl:space-x-10"
            >
              {navLinks.map((link, index) => {
                const isActive = isActiveLink(link.href);
                return (
                  <motion.li
                    key={link.name}
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.3, delay: 0.2 + index * 0.05 }}
                  >
                    <Link href={link.href}>
                      <motion.span 
                        className={`relative font-medium py-2 transition-colors duration-300 cursor-pointer block text-sm xl:text-base ${
                          isActive ? 'text-white font-semibold' : 'text-slate-300'
                        }`}
                        onMouseEnter={() => setHoveredLink(link.name)}
                        onMouseLeave={() => setHoveredLink('')}
                        whileHover={{ 
                          color: '#3b82f6',
                          transition: { duration: 0.15 }
                        }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {link.name}
                        
                        {/* Active underline */}
                        {isActive && (
                          <motion.div
                            layoutId="activeUnderline"
                            className="absolute bottom-0 left-0 w-full h-0.5 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-sm"
                            initial={false}
                            transition={{ type: "spring", stiffness: 400, damping: 25 }}
                          />
                        )}
                        
                        {/* Hover underline */}
                        {hoveredLink === link.name && !isActive && (
                          <motion.div
                            className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-400/50 rounded-sm"
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: 1 }}
                            exit={{ scaleX: 0 }}
                            transition={{ duration: 0.15 }}
                          />
                        )}
                      </motion.span>
                    </Link>
                  </motion.li>
                );
              })}
            </motion.ul>
            
            {/* Desktop Action Buttons */}
            <motion.div 
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="hidden sm:flex items-center space-x-3 lg:space-x-4"
            >
              <motion.button 
                onClick={handleSignUpClick}
                whileHover={{ 
                  scale: 1.03,
                  boxShadow: "0 8px 20px rgba(59, 130, 246, 0.4)",
                  y: -1
                }}
                whileTap={{ scale: 0.98 }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white font-semibold px-4 lg:px-6 py-2 lg:py-2.5 rounded-lg transition-all duration-200 shadow-lg shadow-blue-500/25 text-sm lg:text-base"
              >
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  Sign Up
                </motion.span>
              </motion.button>
              
              <motion.button 
                onClick={handleLogInClick}
                whileHover={{ 
                  scale: 1.03,
                  borderColor: '#3b82f6',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  color: '#ffffff'
                }}
                whileTap={{ scale: 0.98 }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
                className="border-2 border-blue-500/30 text-slate-300 font-semibold px-4 lg:px-6 py-2 lg:py-2.5 rounded-lg transition-all duration-200 text-sm lg:text-base"
              >
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.35 }}
                >
                  Login
                </motion.span>
              </motion.button>
            </motion.div>

            {/* Mobile Menu Button */}
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.25 }}
              onClick={toggleMobileMenu}
              className="lg:hidden p-2 rounded-lg border border-blue-500/30 text-slate-300 hover:text-white hover:border-blue-500/50 transition-colors duration-200"
              aria-label="Toggle menu"
            >
              <motion.div
                animate={isMobileMenuOpen ? "open" : "closed"}
                className="w-6 h-6 flex flex-col justify-center items-center"
              >
                <motion.span
                  variants={{
                    closed: { rotate: 0, y: 0 },
                    open: { rotate: 45, y: 6 }
                  }}
                  className="w-6 h-0.5 bg-current block transition-all duration-200 origin-center"
                />
                <motion.span
                  variants={{
                    closed: { opacity: 1 },
                    open: { opacity: 0 }
                  }}
                  className="w-6 h-0.5 bg-current block mt-1.5 transition-all duration-200"
                />
                <motion.span
                  variants={{
                    closed: { rotate: 0, y: 0 },
                    open: { rotate: -45, y: -6 }
                  }}
                  className="w-6 h-0.5 bg-current block mt-1.5 transition-all duration-200 origin-center"
                />
              </motion.div>
            </motion.button>
          </div>
        </motion.div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2, ease: "easeInOut" }}
              className="lg:hidden relative z-20 bg-slate-900/95 backdrop-blur-sm border-t border-blue-500/20"
            >
              <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4">
                {/* Mobile Navigation Links */}
                <motion.ul className="space-y-1 mb-6">
                  {navLinks.map((link, index) => {
                    const isActive = isActiveLink(link.href);
                    return (
                      <motion.li
                        key={link.name}
                        initial={{ x: -30, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                      >
                        <Link href={link.href} onClick={closeMobileMenu}>
                          <motion.span 
                            className={`flex items-center justify-between py-3 px-4 rounded-lg transition-all duration-200 ${
                              isActive 
                                ? 'text-white bg-blue-500/20 border-l-4 border-blue-500' 
                                : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                            }`}
                            whileTap={{ scale: 0.99 }}
                          >
                            <span className="font-medium">{link.name}</span>
                            {isActive && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="w-2 h-2 bg-blue-500 rounded-full"
                              />
                            )}
                          </motion.span>
                        </Link>
                      </motion.li>
                    );
                  })}
                </motion.ul>

                {/* Mobile Action Buttons */}
                <motion.div 
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  className="flex flex-col space-y-3 sm:hidden"
                >
                  <motion.button 
                    onClick={handleSignUpClick}
                    whileTap={{ scale: 0.99 }}
                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-3 rounded-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
                  >
                    Sign Up
                  </motion.button>
                  
                  <motion.button 
                    onClick={handleLogInClick}
                    whileTap={{ scale: 0.99 }}
                    className="w-full border-2 border-blue-500/30 text-slate-300 font-semibold py-3 rounded-lg transition-all duration-200 hover:border-blue-500/50 hover:bg-blue-500/10"
                  >
                    Login
                  </motion.button>
                </motion.div>

                {/* Mobile Action Buttons for SM screens */}
                <motion.div 
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  className="hidden sm:flex lg:hidden flex-row space-x-4 justify-center"
                >
                  <motion.button 
                    onClick={handleSignUpClick}
                    whileTap={{ scale: 0.99 }}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-3 rounded-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
                  >
                    Sign Up
                  </motion.button>
                  
                  <motion.button 
                    onClick={handleLogInClick}
                    whileTap={{ scale: 0.99 }}
                    className="flex-1 border-2 border-blue-500/30 text-slate-300 font-semibold py-3 rounded-lg transition-all duration-200 hover:border-blue-500/50 hover:bg-blue-500/10"
                  >
                    Login
                  </motion.button>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Auth Modals */}
      <AuthModals
        showSignUp={showSignUp}
        showLogIn={showLogIn}
        onCloseSignUp={handleCloseSignUp}
        onCloseLogIn={handleCloseLogIn}
        onSwitchToLogIn={handleSwitchToLogIn}
        onSwitchToSignUp={handleSwitchToSignUp}
      />
    </>
  );
};

export default Navbar;