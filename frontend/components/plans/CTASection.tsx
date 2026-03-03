"use client";

import React from 'react';
import { motion } from 'framer-motion';

const CTASection = () => {
  // Faster animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.05
      }
    }
  };

  const textVariants = {
    hidden: { 
      y: 20, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  return (
    <section className="relative py-10 sm:py-16 md:py-20">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-cyan-600/10"></div>
      
      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 text-center">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="space-y-6 sm:space-y-8"
        >
          <motion.h2
            variants={textVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white leading-tight"
          >
            Ready to Start Trading with
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent"> AI Bots?</span>
          </motion.h2>
          
          <motion.p
            variants={textVariants}
            className="text-base sm:text-lg lg:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed px-4"
          >
            Join thousands of traders already using our AI bots to maximize their profits. Start your free trial today.
          </motion.p>
          
          <motion.div
            variants={textVariants}
            className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center px-4"
          >
            <motion.button
              whileHover={{ 
                scale: 1.02,
                boxShadow: "0 10px 30px rgba(59, 130, 246, 0.3)"
              }}
              whileTap={{ scale: 0.98 }}
              className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-lg sm:rounded-xl font-semibold text-sm sm:text-base lg:text-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
            >
              Start 7-Day Free Trial
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full sm:w-auto border border-blue-500/50 hover:border-blue-400 text-blue-400 hover:text-blue-300 px-6 sm:px-8 py-3 sm:py-4 rounded-lg sm:rounded-xl font-semibold text-sm sm:text-base lg:text-lg transition-all duration-200"
            >
              Contact Sales
            </motion.button>
          </motion.div>

          <motion.p
            variants={textVariants}
            className="text-slate-400 text-xs sm:text-sm"
          >
            No credit card required • Cancel anytime • 24/7 Support
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;