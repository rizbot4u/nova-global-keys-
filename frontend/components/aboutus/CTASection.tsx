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
        staggerChildren: 0.03,
        delayChildren: 0.02
      }
    }
  };

  const textVariants = {
    hidden: { 
      y: 15, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.25,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  return (
    <section className="relative py-8 sm:py-12 md:py-16 lg:py-20 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-cyan-600/10"></div>
      
      <div className="relative z-10 max-w-4xl mx-auto px-3 sm:px-4 md:px-6 text-center">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-30px" }}
          className="space-y-4 sm:space-y-6 md:space-y-8"
        >
          <motion.h2
            variants={textVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white px-3 sm:px-4"
          >
            Ready to Start Your
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent"> AI Journey?</span>
          </motion.h2>
          
          <motion.p
            variants={textVariants}
            className="text-base sm:text-lg md:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed px-3 sm:px-4"
          >
            Join thousands of businesses already automating smarter, not harder. Start with our free plan today.
          </motion.p>
          
          <motion.div
            variants={textVariants}
            className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center px-3 sm:px-4"
          >
            <motion.button
              whileHover={{ 
                scale: 1.02,
                boxShadow: "0 15px 30px rgba(59, 130, 246, 0.3)"
              }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
              className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white px-5 sm:px-6 md:px-8 py-3 sm:py-4 rounded-lg sm:rounded-xl font-semibold text-sm sm:text-base md:text-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
            >
              Get Started Free
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={{ duration: 0.15 }}
              className="w-full sm:w-auto border border-blue-500/50 hover:border-blue-400 text-blue-400 hover:text-blue-300 px-5 sm:px-6 md:px-8 py-3 sm:py-4 rounded-lg sm:rounded-xl font-semibold text-sm sm:text-base md:text-lg transition-all duration-200"
            >
              Learn More
            </motion.button>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;