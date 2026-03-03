"use client";

import React from 'react';
import { motion } from 'framer-motion';

const OurStorySection = () => {
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

  const cardVariants = {
    hidden: { 
      y: 20,
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
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 75% 75%, rgba(6, 182, 212, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '45px 45px, 60px 60px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-30px" }}
          className="text-center mb-8 sm:mb-12 md:mb-16"
        >
          <motion.h2
            variants={textVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4 md:mb-6"
          >
            Our Story
          </motion.h2>
          <motion.p
            variants={textVariants}
            className="text-base sm:text-lg md:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed px-3 sm:px-4"
          >
            Whether you're a freelancer, small business owner, or part of a growing team, this platform simplifies the way you use AI. With a wide range of bots for different tasks—marketing, support, productivity—you can instantly enhance your workflow. Each bot is fully customizable to meet your specific needs, helping you stay ahead in a fast-paced digital world.
          </motion.p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-30px" }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8"
        >
          {/* Mission Card */}
          <motion.div
            variants={cardVariants}
            whileHover={{ y: -3 }}
            transition={{ duration: 0.15 }}
            className="group p-4 sm:p-6 md:p-8 rounded-xl sm:rounded-2xl border border-blue-500/20 bg-slate-800/50 backdrop-blur-sm hover:border-blue-400/40 transition-all duration-200"
          >
            <div className="text-2xl sm:text-3xl md:text-4xl mb-3 sm:mb-4">🎯</div>
            <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-white mb-3 sm:mb-4 group-hover:text-blue-400 transition-colors">
              Our Mission
            </h3>
            <p className="text-slate-300 leading-relaxed text-sm sm:text-base">
              To democratize AI automation and make it accessible to businesses of all sizes, helping them scale efficiently and stay competitive in the digital age.
            </p>
          </motion.div>

          {/* Vision Card */}
          <motion.div
            variants={cardVariants}
            whileHover={{ y: -3 }}
            transition={{ duration: 0.15 }}
            className="group p-4 sm:p-6 md:p-8 rounded-xl sm:rounded-2xl border border-blue-500/20 bg-slate-800/50 backdrop-blur-sm hover:border-blue-400/40 transition-all duration-200"
          >
            <div className="text-2xl sm:text-3xl md:text-4xl mb-3 sm:mb-4">🚀</div>
            <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-white mb-3 sm:mb-4 group-hover:text-blue-400 transition-colors">
              Our Vision
            </h3>
            <p className="text-slate-300 leading-relaxed text-sm sm:text-base">
              A world where every business can harness the power of AI without complexity, creating more time for what truly matters - innovation and growth.
            </p>
          </motion.div>

          {/* Values Card */}
          <motion.div
            variants={cardVariants}
            whileHover={{ y: -3 }}
            transition={{ duration: 0.15 }}
            className="group p-4 sm:p-6 md:p-8 rounded-xl sm:rounded-2xl border border-blue-500/20 bg-slate-800/50 backdrop-blur-sm hover:border-blue-400/40 transition-all duration-200 md:col-span-2 lg:col-span-1"
          >
            <div className="text-2xl sm:text-3xl md:text-4xl mb-3 sm:mb-4">💎</div>
            <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-white mb-3 sm:mb-4 group-hover:text-blue-400 transition-colors">
              Our Values
            </h3>
            <p className="text-slate-300 leading-relaxed text-sm sm:text-base">
              Innovation, reliability, and user-centricity drive everything we do. We believe in creating tools that are powerful yet simple to use.
            </p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default OurStorySection;