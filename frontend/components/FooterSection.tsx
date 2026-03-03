"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { ArrowRight, Mail, Phone, MapPin, User, Lock } from 'lucide-react';
import AuthModals from './AuthModals';

const FooterSection = () => {
  const [showSignUp, setShowSignUp] = useState(false);
  const [showLogIn, setShowLogIn] = useState(false);

  const handleSignUpClick = () => {
    setShowSignUp(true);
    setShowLogIn(false);
  };

  const handleLogInClick = () => {
    setShowLogIn(true);
    setShowSignUp(false);
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

  // Animation variants - faster and smoother
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { 
      y: 20, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.4,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const logoVariants = {
    hidden: { scale: 0.9, opacity: 0 },
    visible: { 
      scale: 1, 
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const linkVariants = {
    rest: { x: 0 },
    hover: { 
      x: 3,
      transition: {
        duration: 0.15,
        ease: "easeOut"
      }
    }
  };

  const quickLinks = [
    { name: 'Home', href: '/' },
    { name: 'About Us', href: '/about-us' },
    { name: 'Contact Us', href: '/contact-us' },
    { name: 'Price Charts', href: '/price-charts' },
  ];

  const legalLinks = [
    { name: 'Privacy Policy', href: '/privacy-policy' },
    { name: 'Terms Of Service', href: '/terms-of-service' },
  ];

  return (
    <>
      <footer className="relative bg-gradient-to-b from-slate-900 via-slate-950 to-black pt-12 sm:pt-16 md:pt-20 pb-6 sm:pb-8 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" 
            style={{
              backgroundImage: `
                radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
                radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.1) 1px, transparent 1px),
                radial-gradient(circle at 40% 60%, rgba(59, 130, 246, 0.05) 1px, transparent 1px)
              `,
              backgroundSize: '80px 80px, 60px 60px, 50px 50px'
            }}
          />
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6">
          {/* Main Footer Content */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-30px" }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 sm:gap-10 lg:gap-12 xl:gap-16 mb-10 sm:mb-12 lg:mb-16"
          >
            {/* Company Info Section */}
            <motion.div variants={itemVariants} className="space-y-4 sm:space-y-6 sm:col-span-2 lg:col-span-2">
              {/* Logo */}
              <Link href="/">
                <motion.div
                  variants={logoVariants}
                  whileHover={{ scale: 1.03 }}
                  transition={{ duration: 0.15 }}
                  className="flex items-center space-x-2 sm:space-x-3 cursor-pointer"
                >
                  <div className="relative">
                    <Image
                      src="/images/logo.svg"
                      alt="AI Bot Logo"
                      width={48}
                      height={48}
                      className="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 object-contain"
                      priority
                    />
                    {/* Glowing effect */}
                    <motion.div
                      className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 blur-lg opacity-20 -z-10"
                      animate={{ 
                        scale: [1, 1.05, 1],
                        opacity: [0.2, 0.35, 0.2]
                      }}
                      transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
                    />
                  </div>
                  <span className="text-xl sm:text-2xl font-bold text-white tracking-tight">AI BOT</span>
                </motion.div>
              </Link>

              {/* Description */}
              <motion.p
                variants={itemVariants}
                className="text-slate-400 leading-relaxed text-sm sm:text-base max-w-full sm:max-w-md lg:max-w-sm"
              >
                Advanced AI-powered crypto trading bots designed to automate your trading strategies. Experience 24/7 market monitoring, intelligent risk management, and profitable trading opportunities with our cutting-edge algorithms.
              </motion.p>

              {/* Contact Info */}
              <motion.div variants={itemVariants} className="space-y-2 sm:space-y-3">
                <motion.a
                  href="mailto:support@aibot.com"
                  whileHover={{ x: 3 }}
                  transition={{ duration: 0.15 }}
                  className="flex items-center space-x-2 sm:space-x-3 text-slate-300 hover:text-blue-400 transition-colors duration-150"
                >
                  <Mail size={16} className="sm:w-[18px] sm:h-[18px] text-blue-500 flex-shrink-0" />
                  <span className="text-xs sm:text-sm break-all">support@aibot.com</span>
                </motion.a>
                <motion.a
                  href="tel:+1234567890"
                  whileHover={{ x: 3 }}
                  transition={{ duration: 0.15 }}
                  className="flex items-center space-x-2 sm:space-x-3 text-slate-300 hover:text-blue-400 transition-colors duration-150"
                >
                  <Phone size={16} className="sm:w-[18px] sm:h-[18px] text-blue-500 flex-shrink-0" />
                  <span className="text-xs sm:text-sm">(123) 456-7890</span>
                </motion.a>
                <motion.div
                  whileHover={{ x: 3 }}
                  transition={{ duration: 0.15 }}
                  className="flex items-center space-x-2 sm:space-x-3 text-slate-300"
                >
                  <MapPin size={16} className="sm:w-[18px] sm:h-[18px] text-blue-500 flex-shrink-0" />
                  <span className="text-xs sm:text-sm">Global Service Available</span>
                </motion.div>
              </motion.div>
            </motion.div>

            {/* Quick Links Section */}
            <motion.div variants={itemVariants} className="lg:flex lg:justify-center">
              <div className="space-y-4 sm:space-y-6">
                <motion.h3
                  variants={itemVariants}
                  className="text-lg sm:text-xl font-semibold text-white"
                >
                  Quick Links
                </motion.h3>
                <motion.ul variants={itemVariants} className="space-y-2 sm:space-y-4">
                  {quickLinks.map((link, index) => (
                    <motion.li
                      key={link.name}
                      initial={{ opacity: 0, x: -15 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.05, duration: 0.3 }}
                    >
                      <Link href={link.href}>
                        <motion.span
                          variants={linkVariants}
                          initial="rest"
                          whileHover="hover"
                          className="text-slate-400 hover:text-blue-400 transition-colors duration-150 text-xs sm:text-sm inline-block cursor-pointer"
                        >
                          {link.name}
                        </motion.span>
                      </Link>
                    </motion.li>
                  ))}
                </motion.ul>
              </div>
            </motion.div>

            {/* Auth Section */}
            <motion.div variants={itemVariants} className="space-y-4 sm:space-y-6">
              <motion.h3
                variants={itemVariants}
                className="text-lg sm:text-xl font-semibold text-white"
              >
                Get Started
              </motion.h3>
              
              <motion.div
                variants={itemVariants}
                className="space-y-3 sm:space-y-4"
              >
                <motion.button
                  onClick={handleSignUpClick}
                  whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(59, 130, 246, 0.3)" }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg sm:rounded-xl font-medium flex items-center justify-center space-x-2 transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/25 text-sm sm:text-base"
                >
                  <User size={16} className="sm:w-[18px] sm:h-[18px]" />
                  <span>Sign Up</span>
                  <motion.div
                    animate={{ x: [0, 3, 0] }}
                    transition={{ 
                      duration: 1.2, 
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    <ArrowRight size={16} className="sm:w-[18px] sm:h-[18px]" />
                  </motion.div>
                </motion.button>

                <motion.button
                  onClick={handleLogInClick}
                  whileHover={{ 
                    scale: 1.02, 
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderColor: '#3b82f6'
                  }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full bg-slate-800/60 border border-slate-700/50 text-white py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg sm:rounded-xl font-medium flex items-center justify-center space-x-2 transition-all duration-200 hover:shadow-lg hover:shadow-cyan-500/25 backdrop-blur-sm text-sm sm:text-base"
                >
                  <Lock size={16} className="sm:w-[18px] sm:h-[18px]" />
                  <span>Login</span>
                  <motion.div
                    animate={{ x: [0, 3, 0] }}
                    transition={{ 
                      duration: 1.2, 
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 0.4
                    }}
                  >
                    <ArrowRight size={16} className="sm:w-[18px] sm:h-[18px]" />
                  </motion.div>
                </motion.button>
              </motion.div>

              {/* Additional Info */}
              <motion.div
                variants={itemVariants}
                className="pt-2 sm:pt-4 text-xs text-slate-500 space-y-1 sm:space-y-2"
              >
                <p>✓ No hidden fees</p>
                <p>✓ 24/7 customer support</p>
                <p>✓ Secure & encrypted</p>
              </motion.div>
            </motion.div>
          </motion.div>

          {/* Bottom Border */}
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent mb-6 sm:mb-8 origin-center"
          />

          {/* Footer Bottom */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="flex flex-col sm:flex-row justify-between items-center space-y-3 sm:space-y-0 text-center sm:text-left"
          >
            <motion.p
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.15 }}
              className="text-slate-500 text-xs sm:text-sm"
            >
              Copyright © 2025 AI Bot. All Rights Reserved.
            </motion.p>
            
            <motion.div
              className="flex items-center space-x-4 sm:space-x-6 text-xs sm:text-sm"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <Link href="/privacy-policy">
                <motion.span
                  variants={linkVariants}
                  initial="rest"
                  whileHover="hover"
                  className="text-slate-500 hover:text-blue-400 transition-colors duration-150 cursor-pointer whitespace-nowrap"
                >
                  Privacy Policy
                </motion.span>
              </Link>
              <span className="text-slate-700">|</span>
              <Link href="/terms-of-service">
                <motion.span
                  variants={linkVariants}
                  initial="rest"
                  whileHover="hover"
                  className="text-slate-500 hover:text-blue-400 transition-colors duration-150 cursor-pointer whitespace-nowrap"
                >
                  Terms Of Service
                </motion.span>
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </footer>

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

export default FooterSection;