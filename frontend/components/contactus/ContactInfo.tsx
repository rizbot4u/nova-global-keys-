"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Check, Mail } from 'lucide-react';

const ContactInfo = () => {
  // Faster animation variants
  const leftSectionVariants = {
    hidden: { opacity: 0, x: -30 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  const itemVariants = {
    hidden: { 
      y: 15, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.25,
        ease: "easeOut"
      }
    }
  };

  return (
    <motion.div
      variants={leftSectionVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="space-y-12 sm:space-y-16 order-2 lg:order-1"
    >
      {/* Contact Sales */}
      <div className="space-y-4 sm:space-y-6">
        <motion.h2
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.15 }}
          className="text-xl sm:text-2xl md:text-3xl font-bold text-white"
        >
          Contact Sales
        </motion.h2>
        
        <motion.p
          className="text-slate-400 leading-relaxed text-sm sm:text-base"
          variants={itemVariants}
        >
          Connect with us for custom solutions or product insights.
        </motion.p>

        <div className="space-y-3 sm:space-y-4">
          {[
            "Request a demo",
            "Find the right product for your business", 
            "Onboarding assistance"
          ].map((item, index) => (
            <motion.div
              key={item}
              initial={{ opacity: 0, x: -15 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05, duration: 0.25 }}
              whileHover={{ x: 3 }}
              className="flex items-center space-x-2 sm:space-x-3 group cursor-pointer"
            >
              <motion.div
                whileHover={{ scale: 1.1, rotate: 180 }}
                transition={{ duration: 0.15 }}
                className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0"
              >
                <Check size={10} className="sm:w-3 sm:h-3 text-white" />
              </motion.div>
              <span className="text-white group-hover:text-blue-400 transition-colors duration-150 text-sm sm:text-base">
                {item}
              </span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Support Section */}
      <div className="space-y-4 sm:space-y-6">
        <motion.h2
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.15 }}
          className="text-xl sm:text-2xl md:text-3xl font-bold text-white"
        >
          Support
        </motion.h2>
        
        <motion.p
          className="text-slate-400 leading-relaxed text-sm sm:text-base"
          variants={itemVariants}
        >
          Need help with technical issues or products?
        </motion.p>

        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.15 }}
          className="inline-block"
        >
          <div className="flex items-center space-x-2 sm:space-x-3 p-3 sm:p-4 bg-slate-800/40 backdrop-blur-sm border border-blue-500/30 rounded-lg sm:rounded-xl hover:border-blue-400/50 transition-all duration-200 group cursor-pointer">
            <Mail size={16} className="sm:w-5 sm:h-5 text-blue-400 group-hover:scale-110 transition-transform duration-150" />
            <span className="text-blue-400 group-hover:text-blue-300 transition-colors duration-150 border-b border-blue-400/50 group-hover:border-blue-300/50 text-sm sm:text-base">
              your.mail@gmail.com
            </span>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ContactInfo;