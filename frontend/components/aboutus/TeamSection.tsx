"use client";

import React from 'react';
import { motion } from 'framer-motion';

const TeamSection = () => {
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

  // Team members data
  const teamMembers = [
    {
      name: "Sarah Chen",
      role: "CEO & Founder",
      description: "AI strategist with 10+ years in fintech automation",
      image: "👩‍💼"
    },
    {
      name: "Marcus Rodriguez",
      role: "CTO",
      description: "Expert in machine learning and algorithmic trading systems",
      image: "👨‍💻"
    },
    {
      name: "Emily Watson",
      role: "Head of Product",
      description: "UX specialist focused on making AI accessible to everyone",
      image: "👩‍🎨"
    }
  ];

  return (
    <section className="relative py-8 sm:py-12 md:py-16 lg:py-20 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-500/5 to-transparent"></div>
      
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
            Meet Our Team
          </motion.h2>
          <motion.p
            variants={textVariants}
            className="text-base sm:text-lg md:text-xl text-slate-300 max-w-2xl mx-auto px-3 sm:px-4"
          >
            The passionate minds behind your AI automation success
          </motion.p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-30px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8"
        >
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              variants={cardVariants}
              whileHover={{ y: -3 }}
              transition={{ duration: 0.15 }}
              className="group text-center p-4 sm:p-6 md:p-8 rounded-xl sm:rounded-2xl border border-blue-500/20 bg-slate-800/50 backdrop-blur-sm hover:border-blue-400/40 transition-all duration-200"
            >
              <motion.div
                whileHover={{ scale: 1.05, rotate: 2 }}
                transition={{ duration: 0.15 }}
                className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl mb-3 sm:mb-4 md:mb-6"
              >
                {member.image}
              </motion.div>
              <h3 className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-white mb-1 sm:mb-2 group-hover:text-blue-400 transition-colors">
                {member.name}
              </h3>
              <p className="text-blue-400 font-semibold mb-2 sm:mb-3 md:mb-4 text-xs sm:text-sm md:text-base">{member.role}</p>
              <p className="text-slate-300 leading-relaxed text-xs sm:text-sm md:text-base">{member.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default TeamSection;