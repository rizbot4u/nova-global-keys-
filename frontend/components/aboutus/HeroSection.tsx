"use client";

import React from 'react';
import { motion } from 'framer-motion';
import RobotIllustration from './RobotIllustration';

const HeroSection = () => {
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

  const imageVariants = {
    hidden: { 
      x: 20,
      opacity: 0,
      scale: 0.97
    },
    visible: {
      x: 0,
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.3,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const quoteVariants = {
    hidden: { 
      x: -10,
      opacity: 0 
    },
    visible: {
      x: 0,
      opacity: 1,
      transition: {
        duration: 0.25,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  return (
    <section className="relative py-8 sm:py-12 md:py-16 lg:py-20 xl:py-24 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.15) 1px, transparent 1px),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.15) 1px, transparent 1px),
              radial-gradient(circle at 40% 70%, rgba(59, 130, 246, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '30px 30px, 45px 45px, 25px 25px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 md:gap-10 lg:gap-12 xl:gap-16 items-center">
          {/* Left Content */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-30px" }}
            className="space-y-4 sm:space-y-6 md:space-y-8 order-2 lg:order-1"
          >
            {/* Section Label */}
            <motion.p
              variants={textVariants}
              className="text-slate-400 text-sm sm:text-base md:text-lg font-medium tracking-wide"
            >
              About Us
            </motion.p>

            {/* Main Heading */}
            <motion.h1
              variants={textVariants}
              className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-white leading-tight"
            >
              The Story So Far
            </motion.h1>

            {/* Quote */}
            <motion.blockquote
              variants={quoteVariants}
              className="relative border-l-4 border-blue-500 pl-3 sm:pl-4 md:pl-6 my-4 sm:my-6 md:my-8"
            >
              <motion.div
                initial={{ scaleY: 0 }}
                whileInView={{ scaleY: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: 0.15 }}
                className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-blue-500 to-cyan-500 origin-top"
              />
              <p className="text-slate-300 text-base sm:text-lg md:text-xl italic leading-relaxed">
                "Success isn't about doing everything yourself. It's about knowing what to automate and when. Let AI be your smartest team member, working around the clock to help you grow faster and smarter."
              </p>
            </motion.blockquote>

            {/* Description Paragraphs */}
            <motion.div
              variants={textVariants}
              className="space-y-3 sm:space-y-4 md:space-y-6"
            >
              <p className="text-slate-300 leading-relaxed text-sm sm:text-base md:text-lg">
                Discover a powerful platform that offers ready-to-use AI bots for businesses, creators, and entrepreneurs. From automating customer service to generating content, these bots are designed to save time and boost efficiency.
              </p>
            </motion.div>
          </motion.div>

          {/* Right Image */}
          <motion.div
            variants={imageVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-30px" }}
            className="relative flex justify-center lg:justify-end mt-6 sm:mt-8 lg:mt-0 order-1 lg:order-2"
          >
            <RobotIllustration />
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;