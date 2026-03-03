"use client";

import React from 'react';
import { motion } from 'framer-motion';

const AllBotsSection = () => {
  // Bot data
  const bots = [
    {
      id: 1,
      name: "DCA Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <rect x="6" y="8" width="36" height="32" rx="4" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <rect x="10" y="12" width="28" height="20" rx="2" fill="#06b6d4" fillOpacity="0.1"/>
          <circle cx="16" cy="18" r="2" fill="#06b6d4"/>
          <circle cx="24" cy="18" r="2" fill="#06b6d4"/>
          <path d="M14 26h20M14 30h16" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M32 18l4-4M32 18l4 4M32 18h8" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      )
    },
    {
      id: 2,
      name: "DCA Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="18" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <circle cx="24" cy="24" r="12" fill="#06b6d4" fillOpacity="0.1"/>
          <path d="M24 12v24M12 24h24" stroke="#3b82f6" strokeWidth="2"/>
          <circle cx="24" cy="16" r="2" fill="#06b6d4"/>
          <circle cx="24" cy="32" r="2" fill="#06b6d4"/>
          <circle cx="16" cy="24" r="2" fill="#06b6d4"/>
          <circle cx="32" cy="24" r="2" fill="#06b6d4"/>
        </svg>
      )
    },
    {
      id: 3,
      name: "DCA Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <rect x="8" y="10" width="32" height="28" rx="3" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <rect x="12" y="14" width="24" height="16" rx="2" fill="#06b6d4" fillOpacity="0.1"/>
          <path d="M16 20l6 4 10-8" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="18" cy="34" r="2" fill="#06b6d4"/>
          <circle cx="24" cy="34" r="2" fill="#06b6d4"/>
          <circle cx="30" cy="34" r="2" fill="#06b6d4"/>
        </svg>
      )
    },
    {
      id: 4,
      name: "DC Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <rect x="6" y="12" width="36" height="24" rx="4" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <rect x="10" y="16" width="28" height="16" rx="2" fill="#06b6d4" fillOpacity="0.1"/>
          <path d="M16 22l4 3 4-3 4 3 4-3" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="14" cy="28" r="1.5" fill="#06b6d4"/>
          <circle cx="20" cy="28" r="1.5" fill="#06b6d4"/>
          <circle cx="26" cy="28" r="1.5" fill="#06b6d4"/>
          <circle cx="32" cy="28" r="1.5" fill="#06b6d4"/>
        </svg>
      )
    },
    {
      id: 5,
      name: "DC Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="16" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <circle cx="24" cy="24" r="8" fill="#06b6d4" fillOpacity="0.1"/>
          <path d="M24 8v6M24 34v6M8 24h6M34 24h6" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round"/>
          <path d="M35.5 12.5l-4.5 4.5M17 17l-4.5-4.5M12.5 35.5l4.5-4.5M31 31l4.5 4.5" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      )
    },
    {
      id: 6,
      name: "DC Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <rect x="10" y="10" width="28" height="28" rx="6" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <rect x="14" y="14" width="20" height="20" rx="4" fill="#06b6d4" fillOpacity="0.1"/>
          <path d="M20 22h8M18 26h12M22 30h4" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="32" cy="16" r="3" stroke="#06b6d4" strokeWidth="1.5" fill="none"/>
          <path d="M30.5 14.5l3 3" stroke="#3b82f6" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      )
    },
    {
      id: 7,
      name: "DC Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <polygon points="24,8 36,20 24,32 12,20" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <polygon points="24,14 30,20 24,26 18,20" fill="#06b6d4" fillOpacity="0.1"/>
          <path d="M24 20h12M6 20h12" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="40" cy="20" r="2" fill="#06b6d4"/>
          <circle cx="8" cy="20" r="2" fill="#06b6d4"/>
          <path d="M24 8v-4M24 40v4" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      )
    },
    {
      id: 8,
      name: "DC Bot",
      description: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim",
      icon: (
        <svg className="w-10 h-10 sm:w-12 sm:h-12" viewBox="0 0 48 48" fill="none">
          <rect x="8" y="8" width="32" height="32" rx="6" stroke="#06b6d4" strokeWidth="2" fill="none"/>
          <rect x="12" y="12" width="24" height="24" rx="4" fill="#06b6d4" fillOpacity="0.1"/>
          <circle cx="20" cy="20" r="3" stroke="#3b82f6" strokeWidth="2" fill="none"/>
          <circle cx="28" cy="28" r="3" stroke="#3b82f6" strokeWidth="2" fill="none"/>
          <path d="M22.5 22.5l3 3" stroke="#06b6d4" strokeWidth="2" strokeLinecap="round"/>
          <path d="M16 32h16M16 16h6" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      )
    }
  ];

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

  const titleVariants = {
    hidden: { 
      y: 30, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const cardVariants = {
    hidden: { 
      y: 40,
      opacity: 0,
      scale: 0.95
    },
    visible: {
      y: 0,
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const BotCard = ({ bot, index }: { bot: typeof bots[0]; index: number }) => (
    <motion.div
      variants={cardVariants}
      whileHover={{ 
        scale: 1.02,
        y: -4,
        transition: { duration: 0.2, ease: "easeOut" }
      }}
      whileTap={{ scale: 0.98 }}
      className="group relative"
    >
      {/* Glowing background effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        whileHover={{ scale: 1.02 }}
      />
      
      {/* Card content */}
      <div className="relative bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl sm:rounded-2xl p-4 sm:p-6 lg:p-8 h-full group-hover:border-blue-500/30 transition-all duration-300">
        {/* Icon container */}
        <motion.div
          className="mb-4 sm:mb-6"
          whileHover={{ scale: 1.05, rotateY: 5 }}
          transition={{ duration: 0.2 }}
        >
          <div className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 bg-slate-700/50 rounded-lg sm:rounded-xl flex items-center justify-center group-hover:bg-slate-600/50 transition-colors duration-200">
            <motion.div
              animate={{ 
                rotateZ: [0, 3, -3, 0],
              }}
              transition={{ 
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              {bot.icon}
            </motion.div>
          </div>
        </motion.div>

        {/* Bot name */}
        <motion.h3
          className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-3 sm:mb-4 group-hover:text-blue-300 transition-colors duration-200"
          whileHover={{ x: 3 }}
          transition={{ duration: 0.15 }}
        >
          {bot.name}
        </motion.h3>

        {/* Description */}
        <motion.p
          className="text-slate-400 leading-relaxed text-xs sm:text-sm lg:text-base mb-4 sm:mb-6 group-hover:text-slate-300 transition-colors duration-200 line-clamp-3"
          initial={{ opacity: 0.8 }}
          whileHover={{ opacity: 1 }}
        >
          {bot.description}
        </motion.p>

        {/* Bottom accent line */}
        <motion.div
          className="h-0.5 bg-gradient-to-r from-blue-500/50 to-cyan-500/50 rounded-full"
          initial={{ scaleX: 0.3, opacity: 0.5 }}
          whileHover={{ scaleX: 1, opacity: 1 }}
          transition={{ duration: 0.2 }}
        />

        {/* Decorative elements */}
        <motion.div
          className="absolute top-3 right-3 sm:top-4 sm:right-4 w-1.5 h-1.5 sm:w-2 sm:h-2 bg-blue-500/40 rounded-full"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.4, 0.8, 0.4]
          }}
          transition={{ 
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: index * 0.1
          }}
        />
      </div>
    </motion.div>
  );

  return (
    <div className="relative bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 py-12 sm:py-16 md:py-20 lg:py-32 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 80% 70%, rgba(6, 182, 212, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 40% 90%, rgba(59, 130, 246, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px, 70px 70px, 40px 40px'
          }}
        />
      </div>

      {/* Floating network lines */}
      <svg className="absolute inset-0 w-full h-full opacity-5" preserveAspectRatio="none">
        <motion.path
          d="M0,100 Q400,50 800,100 T1600,100"
          stroke="url(#networkGradient)"
          strokeWidth="1"
          fill="none"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 2, ease: "easeInOut" }}
        />
        <motion.path
          d="M0,300 Q600,250 1200,300 T2400,300"
          stroke="url(#networkGradient)"
          strokeWidth="1"
          fill="none"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 2, ease: "easeInOut", delay: 0.3 }}
        />
        <defs>
          <linearGradient id="networkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
            <stop offset="50%" stopColor="#06b6d4" stopOpacity="1" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="text-center mb-10 sm:mb-12 lg:mb-16"
        >
          {/* Section Label */}
          <motion.p
            variants={titleVariants}
            className="text-slate-400 text-sm sm:text-base lg:text-lg font-medium mb-2 sm:mb-4 tracking-wide"
          >
            All AI Bots
          </motion.p>

          {/* Main Heading */}
          <motion.h2
            variants={titleVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-white leading-tight px-2"
          >
            All Possible Trading Bots In{" "}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              One Place
            </span>
          </motion.h2>
        </motion.div>

        {/* Bots Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 xs:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8"
        >
          {bots.map((bot, index) => (
            <BotCard key={bot.id} bot={bot} index={index} />
          ))}
        </motion.div>

        {/* Bottom decorative element */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-10 sm:mt-12 lg:mt-16 flex justify-center"
        >
          <div className="w-16 sm:w-20 lg:w-24 h-0.5 sm:h-1 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full opacity-60" />
        </motion.div>
      </div>
    </div>
  );
};

export default AllBotsSection;