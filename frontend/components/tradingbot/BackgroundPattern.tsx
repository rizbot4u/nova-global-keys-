import React from 'react';
import { motion } from 'framer-motion';

const BackgroundPattern = () => {
  return (
    <>
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-10">
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
      <svg className="fixed inset-0 w-full h-full opacity-5 pointer-events-none" preserveAspectRatio="none">
        <motion.path
          d="M0,100 Q400,50 800,100 T1600,100"
          stroke="url(#networkGradient)"
          strokeWidth="1"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2.5, ease: "easeInOut" }}
        />
        <motion.path
          d="M0,300 Q600,250 1200,300 T2400,300"
          stroke="url(#networkGradient)"
          strokeWidth="1"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2.5, ease: "easeInOut", delay: 0.3 }}
        />
        <motion.path
          d="M0,500 Q300,450 600,500 T1200,500"
          stroke="url(#networkGradient)"
          strokeWidth="0.5"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2.5, ease: "easeInOut", delay: 0.6 }}
        />
        <defs>
          <linearGradient id="networkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
            <stop offset="50%" stopColor="#06b6d4" stopOpacity="1" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </>
  );
};

export default BackgroundPattern;