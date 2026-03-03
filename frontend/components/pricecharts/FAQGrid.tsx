"use client";

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface FAQGridProps {
  openFAQ: number | null;
  setOpenFAQ: (index: number | null) => void;
}

const FAQGrid = ({ openFAQ, setOpenFAQ }: FAQGridProps) => {
  // FAQ data
  const faqs = [
    {
      question: "How do I update my billing information?",
      answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec ante vitae purus tempus egestas. Curabitur euismod purus sed elit faucibus. Vivamus ut ante sed libero feugiat fermentum."
    },
    {
      question: "How do I update my billing information?",
      answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec ante vitae purus tempus egestas. Curabitur euismod purus sed elit faucibus. Vivamus ut ante sed libero feugiat fermentum."
    },
    {
      question: "How do I update my billing information?",
      answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec ante vitae purus tempus egestas. Curabitur euismod purus sed elit faucibus. Vivamus ut ante sed libero feugiat fermentum."
    },
    {
      question: "How do I update my billing information?",
      answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec ante vitae purus tempus egestas. Curabitur euismod purus sed elit faucibus. Vivamus ut ante sed libero feugiat fermentum."
    }
  ];

  // Faster animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { 
      y: 20, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  const faqVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: {
        duration: 0.25,
        ease: "easeOut"
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-20"
    >
      {/* FAQ Header */}
      <motion.div variants={itemVariants} className="space-y-4 sm:space-y-6">
        <motion.h2
          className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white leading-tight"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.1 }}
        >
          Got questions?{" "}
          <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            We've got answers.
          </span>
        </motion.h2>
        
        <motion.p
          variants={itemVariants}
          className="text-slate-400 leading-relaxed text-base sm:text-lg"
        >
          Trusted in more than 100 countries and 4 million customers.
        </motion.p>
      </motion.div>

      {/* FAQ Items */}
      <motion.div variants={itemVariants} className="space-y-3 sm:space-y-4">
        {faqs.map((faq, index) => (
          <motion.div
            key={index}
            variants={faqVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            transition={{ delay: index * 0.05 }}
            className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-lg sm:rounded-xl overflow-hidden hover:border-blue-500/30 transition-all duration-200"
          >
            <motion.button
              onClick={() => setOpenFAQ(openFAQ === index ? null : index)}
              whileHover={{ backgroundColor: "rgba(59, 130, 246, 0.05)" }}
              className="w-full p-4 sm:p-6 text-left flex items-center justify-between group"
            >
              <h3 className="text-white font-medium text-sm sm:text-base lg:text-lg pr-4 group-hover:text-blue-400 transition-colors duration-200">
                {faq.question}
              </h3>
              <motion.div
                animate={{ rotate: openFAQ === index ? 180 : 0 }}
                transition={{ duration: 0.2 }}
                className="text-blue-400 flex-shrink-0"
              >
                <ChevronDown size={20} className="sm:w-6 sm:h-6" />
              </motion.div>
            </motion.button>
            
            <AnimatePresence>
              {openFAQ === index && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2, ease: "easeInOut" }}
                  className="overflow-hidden"
                >
                  <div className="px-4 sm:px-6 pb-4 sm:pb-6 border-t border-slate-700/50">
                    <motion.p
                      initial={{ y: -5, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.05, duration: 0.2 }}
                      className="text-slate-400 leading-relaxed pt-3 sm:pt-4 text-sm sm:text-base"
                    >
                      {faq.answer}
                    </motion.p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
};

export default FAQGrid;