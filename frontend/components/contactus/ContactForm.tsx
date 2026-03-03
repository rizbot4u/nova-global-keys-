"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    message: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitted(true);
    setTimeout(() => {
      setIsSubmitted(false);
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        message: ''
      });
    }, 3000);
  };

  // Faster animation variants
  const formVariants = {
    hidden: { opacity: 0, x: 30 },
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
      variants={formVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="space-y-6 sm:space-y-8 order-1 lg:order-2"
    >
      <div className="bg-slate-800/40 backdrop-blur-sm border border-blue-500/20 rounded-xl sm:rounded-2xl p-4 sm:p-6 md:p-8 shadow-2xl shadow-blue-500/10">
        <motion.h3
          variants={itemVariants}
          className="text-xl sm:text-2xl font-bold text-white mb-2"
        >
          Let's Begin The Discussion
        </motion.h3>
        
        <motion.p
          variants={itemVariants}
          className="text-slate-400 mb-6 sm:mb-8 leading-relaxed text-sm sm:text-base"
        >
          Orci phasellus egestas tellus rutrum. Euismod quis{" "}
          <br className="hidden sm:block" />
          viverra nibh cras pulvinar mattis nunc sed.
        </motion.p>

        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
          {/* Name Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <motion.div
              whileFocus={{ scale: 1.01 }}
              transition={{ duration: 0.15 }}
              className="relative group"
            >
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                placeholder="First Name"
                className="w-full px-3 sm:px-4 py-3 sm:py-4 bg-slate-900/60 border border-slate-700/50 rounded-lg sm:rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 text-sm sm:text-base"
                required
              />
              <motion.div
                className="absolute inset-0 rounded-lg sm:rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100"
                transition={{ duration: 0.15 }}
              />
            </motion.div>
            
            <motion.div
              whileFocus={{ scale: 1.01 }}
              transition={{ duration: 0.15 }}
              className="relative group"
            >
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                placeholder="Last Name"
                className="w-full px-3 sm:px-4 py-3 sm:py-4 bg-slate-900/60 border border-slate-700/50 rounded-lg sm:rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 text-sm sm:text-base"
                required
              />
              <motion.div
                className="absolute inset-0 rounded-lg sm:rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100"
                transition={{ duration: 0.15 }}
              />
            </motion.div>
          </div>

          {/* Email Field */}
          <motion.div
            whileFocus={{ scale: 1.01 }}
            transition={{ duration: 0.15 }}
            className="relative group"
          >
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Enter email"
              className="w-full px-3 sm:px-4 py-3 sm:py-4 bg-slate-900/60 border border-slate-700/50 rounded-lg sm:rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 text-sm sm:text-base"
              required
            />
            <motion.div
              className="absolute inset-0 rounded-lg sm:rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100"
              transition={{ duration: 0.15 }}
            />
          </motion.div>

          {/* Message Field */}
          <motion.div
            whileFocus={{ scale: 1.01 }}
            transition={{ duration: 0.15 }}
            className="relative group"
          >
            <textarea
              name="message"
              value={formData.message}
              onChange={handleInputChange}
              placeholder="Message"
              rows={5}
              className="w-full px-3 sm:px-4 py-3 sm:py-4 bg-slate-900/60 border border-slate-700/50 rounded-lg sm:rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 resize-none text-sm sm:text-base"
              required
            />
            <motion.div
              className="absolute inset-0 rounded-lg sm:rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 opacity-0 pointer-events-none group-focus-within:opacity-100"
              transition={{ duration: 0.15 }}
            />
          </motion.div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={isSubmitted}
            whileHover={{ 
              scale: 1.01, 
              boxShadow: "0 0 20px rgba(59, 130, 246, 0.4)" 
            }}
            whileTap={{ scale: 0.99 }}
            transition={{ duration: 0.15 }}
            className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-3 sm:py-4 px-6 sm:px-8 rounded-lg sm:rounded-xl font-semibold text-base sm:text-lg flex items-center justify-center space-x-2 sm:space-x-3 transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>{isSubmitted ? 'Request Sent!' : 'Submit Request'}</span>
            <motion.div
              animate={isSubmitted ? { rotate: 360 } : { x: [0, 3, 0] }}
              transition={{ 
                duration: isSubmitted ? 0.25 : 1, 
                repeat: isSubmitted ? 0 : Infinity,
                ease: "easeInOut"
              }}
            >
              <Send size={16} className="sm:w-5 sm:h-5" />
            </motion.div>
          </motion.button>
        </form>
      </div>
    </motion.div>
  );
};

export default ContactForm;