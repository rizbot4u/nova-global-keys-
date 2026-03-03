"use client";
import { motion } from 'framer-motion';

export default function RobotIllustration() {
  return (
    <div className="relative w-full max-w-[500px] h-[500px] flex items-center justify-center">
      {/* Glow Effect */}
      <div className="absolute w-72 h-72 bg-blue-500/20 rounded-full blur-[100px]" />
      
      <motion.div
        animate={{ y: [0, -20, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        className="relative z-10"
      >
        <svg viewBox="0 0 200 200" className="w-full h-full drop-shadow-[0_0_30px_rgba(59,130,246,0.5)]">
          {/* Warrior Bot Body */}
          <rect x="60" y="60" width="80" height="90" rx="15" fill="#1e293b" stroke="#3b82f6" strokeWidth="2" />
          <rect x="70" y="70" width="60" height="40" rx="5" fill="#0f172a" />
          {/* Eyes */}
          <motion.circle 
            animate={{ opacity: [1, 0.2, 1] }} 
            transition={{ duration: 2, repeat: Infinity }}
            cx="85" cy="90" r="4" fill="#60a5fa" 
          />
          <motion.circle 
            animate={{ opacity: [1, 0.2, 1] }} 
            transition={{ duration: 2, repeat: Infinity }}
            cx="115" cy="90" r="4" fill="#60a5fa" 
          />
          {/* Arms/Shield */}
          <path d="M40,100 L60,90 L60,130 L40,140 Z" fill="#334155" stroke="#3b82f6" />
          <path d="M160,100 L140,90 L140,130 L160,140 Z" fill="#334155" stroke="#3b82f6" />
        </svg>
      </motion.div>
    </div>
  );
}
