"use client";

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const StatsSection = () => {
  // Counter animation hook
  const useCounter = (end: number, duration: number = 1500, delay: number = 0) => {
    const [count, setCount] = useState(0);
    const [hasStarted, setHasStarted] = useState(false);

    useEffect(() => {
      if (!hasStarted) return;

      let startTime: number;
      let animationFrame: number;

      const animate = (currentTime: number) => {
        if (!startTime) startTime = currentTime;
        const progress = Math.min((currentTime - startTime) / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        setCount(Math.floor(end * easeOutQuart));

        if (progress < 1) {
          animationFrame = requestAnimationFrame(animate);
        }
      };

      const timer = setTimeout(() => {
        animationFrame = requestAnimationFrame(animate);
      }, delay);

      return () => {
        clearTimeout(timer);
        cancelAnimationFrame(animationFrame);
      };
    }, [end, duration, delay, hasStarted]);

    return { count, startAnimation: () => setHasStarted(true) };
  };

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

  const headingVariants = {
    hidden: { 
      y: 30, 
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

  const descriptionVariants = {
    hidden: { 
      y: 20, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut",
        delay: 0.1
      }
    }
  };

  const cardVariants = {
    hidden: { 
      y: 40,
      opacity: 0,
      scale: 0.95
    },
    visible: {
      y: 0,
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  const StatCard = ({ 
    number, 
    suffix = "", 
    label, 
    delay = 0 
  }: { 
    number: number; 
    suffix?: string; 
    label: string; 
    delay?: number;
  }) => {
    const { count, startAnimation } = useCounter(number, 1500, delay);

    return (
      <motion.div
        variants={cardVariants}
        whileInView={() => {
          startAnimation();
          return {};
        }}
        viewport={{ once: true, margin: "-50px" }}
        whileHover={{ 
          scale: 1.05,
          y: -8,
          transition: { duration: 0.2, ease: "easeOut" }
        }}
        className="relative group"
      >
        {/* Glowing background effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-xl sm:rounded-2xl blur-xl"
          whileHover={{ 
            scale: 1.1,
            opacity: 1.5,
            transition: { duration: 0.2 }
          }}
        />
        
        {/* Card content */}
        <div className="relative bg-slate-800/60 backdrop-blur-sm border border-blue-500/20 rounded-xl sm:rounded-2xl p-6 sm:p-8 md:p-10 text-center group-hover:border-blue-400/40 transition-all duration-300">
          {/* Animated border glow */}
          <motion.div
            className="absolute inset-0 rounded-xl sm:rounded-2xl bg-gradient-to-r from-blue-500/20 to-cyan-500/20 opacity-0 group-hover:opacity-100 blur-sm transition-opacity duration-300"
            style={{ zIndex: -1 }}
          />
          
          {/* Number with suffix */}
          <motion.div className="mb-3 sm:mb-4">
            <span className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              {count.toLocaleString()}
            </span>
            <span className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              {suffix}
            </span>
          </motion.div>
          
          {/* Label */}
          <motion.p 
            className="text-slate-300 text-sm sm:text-base md:text-lg lg:text-xl font-medium leading-relaxed"
            initial={{ opacity: 0.7 }}
            whileHover={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {label}
          </motion.p>
          
          {/* Decorative elements */}
          <motion.div
            className="absolute top-3 right-3 sm:top-4 sm:right-4 w-1.5 h-1.5 sm:w-2 sm:h-2 bg-blue-500 rounded-full opacity-60"
            animate={{ 
              scale: [1, 1.5, 1],
              opacity: [0.6, 1, 0.6]
            }}
            transition={{ 
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute bottom-3 left-3 sm:bottom-4 sm:left-4 w-1 h-1 sm:w-1.5 sm:h-1.5 bg-cyan-500 rounded-full opacity-60"
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.6, 1, 0.6]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.3
            }}
          />
        </div>
      </motion.div>
    );
  };

  return (
    <div className="relative bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 py-12 sm:py-16 lg:py-20 xl:py-32 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-15">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 75% 75%, rgba(6, 182, 212, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px, 40px 40px, 30px 30px'
          }}
        />
      </div>

      {/* Floating particles */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-0.5 h-0.5 sm:w-1 sm:h-1 bg-blue-500/30 rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [-15, 15, -15],
            opacity: [0.3, 0.8, 0.3],
          }}
          transition={{
            duration: 2 + Math.random() * 1.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: Math.random() * 1.5,
          }}
        />
      ))}

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="text-center mb-12 sm:mb-16 lg:mb-20"
        >
          {/* Main Heading */}
          <motion.h2
            variants={headingVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-bold text-white mb-6 sm:mb-8 leading-tight px-4"
          >
            Empowering Millions Of Traders{" "}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Since 2025
            </span>
          </motion.h2>

          {/* Description */}
          <motion.p
            variants={descriptionVariants}
            className="text-slate-300 text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl leading-relaxed max-w-5xl mx-auto px-4"
          >
            We've built a trusted ecosystem for traders worldwide—offering advanced tools, intelligent automation, and real-time data to maximize profitability. Our commitment to innovation drives smarter, faster, and more strategic trading decisions.
          </motion.p>
        </motion.div>

        {/* Statistics Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8 lg:gap-12"
        >
          <StatCard 
            number={100} 
            suffix="+" 
            label="Traders Registered" 
            delay={100}
          />
          <StatCard 
            number={120} 
            suffix="+" 
            label="Accounts connected" 
            delay={200}
          />
          <StatCard 
            number={200} 
            suffix="%" 
            label="Satisfaction Rate Among buyers" 
            delay={300}
          />
        </motion.div>

        {/* Bottom decorative line */}
        <motion.div
          initial={{ scaleX: 0, opacity: 0 }}
          whileInView={{ scaleX: 1, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.8, ease: "easeOut" }}
          className="mt-12 sm:mt-16 lg:mt-20 mx-auto w-24 sm:w-32 h-0.5 bg-gradient-to-r from-blue-500 to-cyan-500 origin-center"
        />
      </div>
    </div>
  );
};

export default StatsSection;