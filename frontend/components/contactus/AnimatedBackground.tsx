"use client";

import React from 'react';
import { motion } from 'framer-motion';

const AnimatedBackground = () => {
  return (
    <>
      {/* Animated Background Network */}
      <div className="absolute inset-0 opacity-20">
        <motion.div
          animate={{ 
            backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"]
          }}
          transition={{ 
            duration: 15, 
            repeat: Infinity, 
            ease: "linear" 
          }}
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(45deg, transparent 48%, rgba(59, 130, 246, 0.1) 49%, rgba(59, 130, 246, 0.2) 50%, rgba(59, 130, 246, 0.1) 51%, transparent 52%),
              linear-gradient(-45deg, transparent 48%, rgba(6, 182, 212, 0.1) 49%, rgba(6, 182, 212, 0.2) 50%, rgba(6, 182, 212, 0.1) 51%, transparent 52%)
            `,
            backgroundSize: '300px 300px, 450px 450px'
          }}
        />
      </div>

      {/* Floating particles */}
      {[...Array(15)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-0.5 h-0.5 sm:w-1 sm:h-1 bg-blue-400 rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -20, 0],
            opacity: [0, 1, 0],
            scale: [0, 1, 0]
          }}
          transition={{
            duration: 1.5 + Math.random() * 1,
            repeat: Infinity,
            delay: Math.random() * 1.5
          }}
        />
      ))}
    </>
  );
};

export default AnimatedBackground;