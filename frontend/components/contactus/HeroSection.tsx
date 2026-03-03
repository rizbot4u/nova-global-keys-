"use client";

import React from 'react';
import { motion } from 'framer-motion';

const HeroSection = () => {
  // Faster animation variants
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
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="text-left mb-12 sm:mb-16 md:mb-20"
    >
      <motion.h1
        variants={itemVariants}
        className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-white leading-tight mb-4 sm:mb-6 max-w-2xl"
      >
        We&apos;d Love to Hear{" "}
        <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          From You
        </span>
      </motion.h1>
      
      <motion.p
        variants={itemVariants}
        className="text-slate-400 text-base sm:text-lg md:text-xl max-w-xl leading-relaxed"
      >
        Lorem Ipsum Dolor Sit Amet Consectetur Adipiscing{" "}
        <br className="hidden sm:block" />
        Elit Senectus Rutrum, Pretium Nullam Integer Fames
      </motion.p>
    </motion.div>
  );
};

export default HeroSection;