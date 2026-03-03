"use client";

import React from 'react';
import { motion } from 'framer-motion';

const HowWeWorkSection = () => {
  const steps = [
    {
      id: 1,
      title: "Sign Up & Profile",
      description: "Create your account with our guided setup process. Access your personalized dashboard instantly.",
      icon: "boxes"
    },
    {
      id: 2,
      title: "Personalisation",
      description: "Tell us your goals and preferences. We'll customize your experience with AI-driven insights.",
      icon: "cube"
    },
    {
      id: 3,
      title: "Analyse & Buy",
      description: "Monitor your success through clear analytics. Scale what works and optimize for growth.",
      icon: "blocks"
    },
    {
      id: 4,
      title: "Voice AI CS.",
      description: "Voice-based AI assistants that seamlessly handle inbound customer calls and provide personalised support, 24/7.",
      icon: "waveform"
    }
  ];

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1
      }
    }
  };

  const cardVariants = {
    hidden: { 
      y: 30, 
      opacity: 0,
      scale: 0.95
    },
    visible: {
      y: 0,
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  // SVG Icon Components
  const BoxesIcon = () => (
    <motion.svg 
      width="60" 
      height="60" 
      viewBox="0 0 80 80" 
      fill="none"
      className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
    >
      <motion.path
        d="M20 25 L35 15 L50 25 L50 40 L35 50 L20 40 Z"
        stroke="#3b82f6"
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
      />
      <motion.path
        d="M30 30 L45 20 L60 30 L60 45 L45 55 L30 45 Z"
        stroke="#06b6d4"
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
      />
      <motion.path
        d="M35 15 L35 50 M50 25 L35 15 L20 25"
        stroke="#3b82f6"
        strokeWidth="1.5"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.6, delay: 0.5, ease: "easeOut" }}
      />
    </motion.svg>
  );

  const CubeIcon = () => (
    <motion.svg 
      width="60" 
      height="60" 
      viewBox="0 0 80 80" 
      fill="none"
      className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20"
      initial={{ rotateY: 0 }}
      animate={{ rotateY: 360 }}
      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
    >
      <motion.path
        d="M25 30 L40 20 L55 30 L55 50 L40 60 L25 50 Z"
        stroke="#3b82f6"
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
      />
      <motion.path
        d="M25 30 L40 40 L55 30 M40 40 L40 60"
        stroke="#06b6d4"
        strokeWidth="2"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.6, delay: 0.5, ease: "easeOut" }}
      />
      <motion.circle
        cx="40"
        cy="35"
        r="3"
        fill="#3b82f6"
        initial={{ scale: 0 }}
        animate={{ scale: [0, 1.2, 1] }}
        transition={{ duration: 0.5, delay: 0.8, ease: "easeOut" }}
      />
    </motion.svg>
  );

  const BlocksIcon = () => (
    <motion.svg 
      width="60" 
      height="60" 
      viewBox="0 0 80 80" 
      fill="none"
      className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20"
    >
      <motion.path
        d="M15 25 L30 15 L45 25 L45 40 L30 50 L15 40 Z"
        stroke="#3b82f6"
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.7, delay: 0.1, ease: "easeOut" }}
      />
      <motion.path
        d="M35 25 L50 15 L65 25 L65 40 L50 50 L35 40 Z"
        stroke="#06b6d4"
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.7, delay: 0.3, ease: "easeOut" }}
      />
      <motion.path
        d="M25 45 L40 35 L55 45 L55 60 L40 70 L25 60 Z"
        stroke="#3b82f6"
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.7, delay: 0.5, ease: "easeOut" }}
      />
      {/* Connection lines */}
      <motion.path
        d="M30 40 L40 45 M50 40 L40 45"
        stroke="#06b6d4"
        strokeWidth="1"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.4, delay: 0.8, ease: "easeOut" }}
      />
    </motion.svg>
  );

  const WaveformIcon = () => (
    <motion.svg 
      width="60" 
      height="60" 
      viewBox="0 0 80 80" 
      fill="none"
      className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20"
    >
      {[...Array(12)].map((_, i) => (
        <motion.rect
          key={i}
          x={10 + i * 5}
          y={40 - (Math.sin(i * 0.5) * 15 + 10)}
          width="3"
          height={Math.sin(i * 0.5) * 15 + 20}
          fill="#3b82f6"
          initial={{ scaleY: 0 }}
          animate={{ 
            scaleY: [0, 1, 0.7, 1, 0.5, 1],
            fill: ["#3b82f6", "#06b6d4", "#3b82f6"]
          }}
          transition={{ 
            duration: 1.5, 
            delay: i * 0.05,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
        />
      ))}
    </motion.svg>
  );

  const getIcon = (iconType) => {
    switch (iconType) {
      case 'boxes': return <BoxesIcon />;
      case 'cube': return <CubeIcon />;
      case 'blocks': return <BlocksIcon />;
      case 'waveform': return <WaveformIcon />;
      default: return <BoxesIcon />;
    }
  };

  return (
    <div className="relative bg-gradient-to-b from-slate-900 to-slate-800 py-12 sm:py-16 lg:py-20 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 75% 75%, rgba(6, 182, 212, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px, 60px 60px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="text-center mb-12 sm:mb-16"
        >
          <motion.p
            initial={{ y: 15, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
            className="text-slate-400 text-base sm:text-lg mb-3 sm:mb-4"
          >
            How We Works
          </motion.p>
          <motion.h2
            initial={{ y: 20, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2, ease: "easeOut" }}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white px-4"
          >
            Explore Our Simple, Easy
            <br className="hidden sm:block" />
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Process
            </span>
          </motion.h2>
        </motion.div>

        {/* Steps Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8"
        >
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              variants={cardVariants}
              whileHover={{ 
                y: -8,
                scale: 1.02,
                transition: { duration: 0.2, ease: "easeOut" }
              }}
              className="relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm border border-blue-500/20 rounded-xl sm:rounded-2xl p-4 sm:p-6 group cursor-pointer"
            >
              {/* Glow effect on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-xl sm:rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              
              {/* Step Badge */}
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: index * 0.05 + 0.2, ease: "easeOut" }}
                className="relative bg-slate-700 text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-semibold mb-4 sm:mb-6 inline-block"
              >
                Step {step.id}
              </motion.div>

              {/* Icon */}
              <motion.div
                initial={{ scale: 0, rotate: -90 }}
                whileInView={{ scale: 1, rotate: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.05 + 0.3, ease: "easeOut" }}
                className="relative mb-4 sm:mb-6 flex justify-center"
              >
                {getIcon(step.icon)}
              </motion.div>

              {/* Content */}
              <motion.div
                initial={{ y: 15, opacity: 0 }}
                whileInView={{ y: 0, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.05 + 0.5, ease: "easeOut" }}
                className="relative"
              >
                <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4 group-hover:text-blue-400 transition-colors duration-300">
                  {step.title}
                </h3>
                <p className="text-sm sm:text-base text-slate-300 leading-relaxed group-hover:text-slate-200 transition-colors duration-300">
                  {step.description}
                </p>
              </motion.div>

              {/* Bottom border effect */}
              <motion.div
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.05 + 0.7, ease: "easeOut" }}
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-cyan-500 transform origin-left rounded-full"
              />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default HowWeWorkSection;