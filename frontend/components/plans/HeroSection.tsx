"use client";

import React from 'react';
import { motion } from 'framer-motion';

interface HeroSectionProps {
  billingCycle: 'monthly' | 'yearly';
  setBillingCycle: (value: 'monthly' | 'yearly') => void;
}

const HeroSection = ({ billingCycle, setBillingCycle }: HeroSectionProps) => {
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
    <section className="relative py-10 sm:py-16 md:py-20 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.15) 1px, transparent 1px),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.15) 1px, transparent 1px),
              radial-gradient(circle at 40% 70%, rgba(59, 130, 246, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px, 50px 50px, 30px 30px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="text-center mb-8 sm:mb-12 lg:mb-16"
        >
          {/* Section Label */}
          <motion.p
            variants={textVariants}
            className="text-slate-400 text-sm sm:text-base lg:text-lg font-medium mb-2 sm:mb-4 tracking-wide"
          >
            Choose Your Plan
          </motion.p>

          {/* Main Heading */}
          <motion.h1
            variants={textVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-white leading-tight mb-4 sm:mb-6"
          >
            Simple, Transparent 
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent"> Pricing</span>
          </motion.h1>

          <motion.p
            variants={textVariants}
            className="text-base sm:text-lg lg:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed mb-8 sm:mb-12 px-4"
          >
            Choose the perfect plan for your trading needs. All plans include our core features with varying levels of bots and support.
          </motion.p>

          {/* Billing Toggle */}
          <motion.div
            variants={textVariants}
            className="flex items-center justify-center space-x-2 sm:space-x-4 mb-8 sm:mb-12 lg:mb-16"
          >
            <span className={`text-sm sm:text-base lg:text-lg font-medium ${billingCycle === 'monthly' ? 'text-white' : 'text-slate-400'}`}>
              Monthly
            </span>
            <motion.button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative w-12 h-6 sm:w-16 sm:h-8 bg-slate-700 rounded-full p-1 transition-colors duration-200"
              whileTap={{ scale: 0.95 }}
            >
              <motion.div
                className="w-4 h-4 sm:w-6 sm:h-6 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full shadow-lg"
                animate={{
                  x: billingCycle === 'yearly' ? (window.innerWidth < 640 ? 24 : 32) : 0
                }}
                transition={{ type: "spring", stiffness: 500, damping: 25 }}
              />
            </motion.button>
            <span className={`text-sm sm:text-base lg:text-lg font-medium ${billingCycle === 'yearly' ? 'text-white' : 'text-slate-400'}`}>
              Yearly
            </span>
            {billingCycle === 'yearly' && (
              <motion.span
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.2 }}
                className="bg-green-500 text-white text-xs sm:text-sm px-2 sm:px-3 py-1 rounded-full font-medium ml-2"
              >
                Save 17%
              </motion.span>
            )}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;