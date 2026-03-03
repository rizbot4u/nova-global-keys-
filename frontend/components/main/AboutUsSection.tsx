"use client";

import React from 'react';
import { motion } from 'framer-motion';

const AboutUsSection = () => {
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
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
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  const imageVariants = {
    hidden: { 
      x: 30,
      opacity: 0,
      scale: 0.95
    },
    visible: {
      x: 0,
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.6,
        ease: "easeOut"
      }
    }
  };

  const quoteVariants = {
    hidden: { 
      x: -15,
      opacity: 0 
    },
    visible: {
      x: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  return (
    <div className="relative bg-gradient-to-b from-slate-900 to-slate-800 py-12 sm:py-16 lg:py-20 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 40% 70%, rgba(59, 130, 246, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px, 60px 60px, 30px 30px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-16 items-center">
          {/* Left Content */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            className="space-y-6 sm:space-y-8 order-2 lg:order-1"
          >
            {/* Section Label */}
            <motion.p
              variants={textVariants}
              className="text-slate-400 text-base sm:text-lg font-medium tracking-wide"
            >
              About Us
            </motion.p>

            {/* Main Heading */}
            <motion.h2
              variants={textVariants}
              className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-white leading-tight"
            >
              The Story So Far
            </motion.h2>

            {/* Quote */}
            <motion.blockquote
              variants={quoteVariants}
              className="relative border-l-4 border-blue-500 pl-4 sm:pl-6 my-6 sm:my-8"
            >
              <motion.div
                initial={{ scaleY: 0 }}
                whileInView={{ scaleY: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.3, ease: "easeOut" }}
                className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-blue-500 to-cyan-500 origin-top"
              />
              <p className="text-slate-300 text-base sm:text-lg italic leading-relaxed">
                "Success isn't about doing everything yourself. It's about knowing what to automate and when. Let AI be your smartest team member, working around the clock to help you grow faster and smarter."
              </p>
            </motion.blockquote>

            {/* Description Paragraphs */}
            <motion.div
              variants={textVariants}
              className="space-y-4 sm:space-y-6"
            >
              <p className="text-slate-300 leading-relaxed text-sm sm:text-base lg:text-lg">
                Discover a powerful website that offers ready-to-use AI bots for businesses, creators, and entrepreneurs. From automating customer service to generating content, these bots are designed to save time and boost efficiency. No coding needed—just choose, customize, and launch. Perfect for scaling your business or streamlining tasks effortlessly. Trusted by users across industries looking to upgrade with smart automation.
              </p>
              
              <p className="text-slate-300 leading-relaxed text-sm sm:text-base lg:text-lg">
                Whether you're a freelancer, small business owner, or part of a growing team, this platform simplifies the way you use AI. With a wide range of bots for different tasks—marketing, support, productivity—you can instantly enhance your workflow. Each bot is fully customizable to meet your specific needs, helping you stay ahead in a fast-paced digital world. Start automating smarter, not harder.
              </p>
            </motion.div>

            {/* CTA Button */}
            <motion.div
              variants={textVariants}
            >
              <motion.button
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px rgba(59, 130, 246, 0.3)",
                  transition: { duration: 0.2 }
                }}
                whileTap={{ scale: 0.98, transition: { duration: 0.1 } }}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-semibold text-base sm:text-lg transition-all duration-300 shadow-lg shadow-blue-500/25 w-full sm:w-auto"
              >
                Read More Story
              </motion.button>
            </motion.div>
          </motion.div>

          {/* Right Image */}
          <motion.div
            variants={imageVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            className="relative flex justify-center lg:justify-end order-1 lg:order-2"
          >
            {/* Glowing background effect */}
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
              className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-full blur-3xl"
            />
            
            {/* Robot/AI Illustration Placeholder */}
            <motion.div
              initial={{ rotateY: -10, scale: 0.95 }}
              whileInView={{ rotateY: 0, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              whileHover={{ 
                rotateY: 3,
                scale: 1.02,
                transition: { duration: 0.2 }
              }}
              className="relative w-full max-w-xs sm:max-w-sm lg:max-w-lg aspect-square"
            >
              {/* AI Robot SVG Illustration */}
              <motion.svg
                width="100%"
                height="100%"
                viewBox="0 0 400 400"
                fill="none"
                className="drop-shadow-2xl"
              >
                {/* Robot Head */}
                <motion.circle
                  cx="200"
                  cy="150"
                  r="80"
                  fill="url(#robotGradient)"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  initial={{ pathLength: 0, opacity: 0 }}
                  whileInView={{ pathLength: 1, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
                />
                
                {/* Robot Eyes */}
                <motion.circle
                  cx="175"
                  cy="135"
                  r="12"
                  fill="#06b6d4"
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: 0.6, ease: "easeOut" }}
                />
                <motion.circle
                  cx="225"
                  cy="135"
                  r="12"
                  fill="#06b6d4"
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: 0.65, ease: "easeOut" }}
                />
                
                {/* Robot Body */}
                <motion.rect
                  x="150"
                  y="220"
                  width="100"
                  height="120"
                  rx="20"
                  fill="url(#robotGradient)"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  initial={{ pathLength: 0, opacity: 0 }}
                  whileInView={{ pathLength: 1, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.7, delay: 0.4, ease: "easeOut" }}
                />
                
                {/* Circuit Lines */}
                <motion.path
                  d="M170 250 L200 250 L200 280 L230 280"
                  stroke="#06b6d4"
                  strokeWidth="2"
                  fill="none"
                  initial={{ pathLength: 0 }}
                  whileInView={{ pathLength: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.8, ease: "easeOut" }}
                />
                <motion.path
                  d="M170 270 L190 270 L190 300 L220 300"
                  stroke="#06b6d4"
                  strokeWidth="2"
                  fill="none"
                  initial={{ pathLength: 0 }}
                  whileInView={{ pathLength: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.9, ease: "easeOut" }}
                />
                
                {/* Arms */}
                <motion.circle
                  cx="100"
                  cy="260"
                  r="25"
                  fill="url(#robotGradient)"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.7, ease: "easeOut" }}
                />
                <motion.circle
                  cx="300"
                  cy="260"
                  r="25"
                  fill="url(#robotGradient)"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.75, ease: "easeOut" }}
                />
                
                {/* Connecting lines */}
                <motion.line
                  x1="150"
                  y1="260"
                  x2="125"
                  y2="260"
                  stroke="#3b82f6"
                  strokeWidth="3"
                  initial={{ pathLength: 0 }}
                  whileInView={{ pathLength: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: 0.8, ease: "easeOut" }}
                />
                <motion.line
                  x1="250"
                  y1="260"
                  x2="275"
                  y2="260"
                  stroke="#3b82f6"
                  strokeWidth="3"
                  initial={{ pathLength: 0 }}
                  whileInView={{ pathLength: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: 0.85, ease: "easeOut" }}
                />
                
                {/* Floating particles */}
                {[...Array(8)].map((_, i) => (
                  <motion.circle
                    key={i}
                    cx={120 + Math.cos(i * 0.785) * 150}
                    cy={200 + Math.sin(i * 0.785) * 100}
                    r="3"
                    fill="#06b6d4"
                    initial={{ scale: 0, opacity: 0 }}
                    whileInView={{ scale: 1, opacity: 0.7 }}
                    viewport={{ once: true }}
                    transition={{ 
                      duration: 0.3, 
                      delay: 1.2 + i * 0.05,
                      repeat: Infinity,
                      repeatType: "reverse",
                      repeatDelay: 0.8,
                      ease: "easeInOut"
                    }}
                  />
                ))}
                
                {/* Gradients */}
                <defs>
                  <linearGradient id="robotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#1e293b" />
                    <stop offset="50%" stopColor="#334155" />
                    <stop offset="100%" stopColor="#1e293b" />
                  </linearGradient>
                </defs>
              </motion.svg>
              
              {/* Pulsing rings around the robot */}
              <motion.div
                className="absolute inset-0 rounded-full border border-blue-500/30"
                initial={{ scale: 0.8, opacity: 0 }}
                whileInView={{ scale: 1.2, opacity: [0, 0.5, 0] }}
                viewport={{ once: true }}
                transition={{ 
                  duration: 1.5,
                  delay: 1.5,
                  repeat: Infinity,
                  repeatDelay: 0.8,
                  ease: "easeInOut"
                }}
              />
              <motion.div
                className="absolute inset-4 rounded-full border border-cyan-500/20"
                initial={{ scale: 0.9, opacity: 0 }}
                whileInView={{ scale: 1.1, opacity: [0, 0.3, 0] }}
                viewport={{ once: true }}
                transition={{ 
                  duration: 1.5,
                  delay: 1.8,
                  repeat: Infinity,
                  repeatDelay: 0.8,
                  ease: "easeInOut"
                }}
              />
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default AboutUsSection;