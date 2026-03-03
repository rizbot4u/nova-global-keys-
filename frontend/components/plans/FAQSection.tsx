"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';

const FAQSection = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

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

  const cardVariants = {
    hidden: { 
      y: 20,
      opacity: 0,
      scale: 0.98
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

  // FAQ data
  const faqs = [
    {
      question: "Can I switch plans anytime?",
      answer: "Yes, you can upgrade or downgrade your plan at any time. Changes will be reflected in your next billing cycle."
    },
    {
      question: "Do you offer a free trial?",
      answer: "We offer a 7-day free trial for all new users on any plan. No credit card required to start."
    },
    {
      question: "What payment methods do you accept?",
      answer: "We accept all major credit cards, PayPal, and cryptocurrency payments including Bitcoin and Ethereum."
    },
    {
      question: "Is there a setup fee?",
      answer: "No setup fees! You only pay the monthly or yearly subscription fee for your chosen plan."
    },
    {
      question: "Can I cancel anytime?",
      answer: "Yes, you can cancel your subscription at any time. You'll continue to have access until the end of your billing period."
    },
    {
      question: "Do you provide customer support?",
      answer: "Yes! We provide email support for Starter, priority support for Professional, and 24/7 dedicated support for Enterprise plans."
    }
  ];

  return (
    <section className="relative py-10 sm:py-16 md:py-20">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-cyan-500/5"></div>
      
      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="text-center mb-8 sm:mb-12 lg:mb-16"
        >
          <motion.h2
            variants={textVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 sm:mb-6"
          >
            Frequently Asked Questions
          </motion.h2>
          <motion.p
            variants={textVariants}
            className="text-base sm:text-lg lg:text-xl text-slate-300 max-w-2xl mx-auto px-4"
          >
            Everything you need to know about our pricing and plans
          </motion.p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="space-y-3 sm:space-y-4"
        >
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              variants={cardVariants}
              className="border border-slate-700/50 rounded-xl sm:rounded-2xl overflow-hidden bg-slate-800/30 backdrop-blur-sm"
            >
              <motion.button
                onClick={() => setOpenFaq(openFaq === index ? null : index)}
                className="w-full px-4 sm:px-6 lg:px-8 py-4 sm:py-6 text-left flex items-center justify-between hover:bg-slate-700/20 transition-colors duration-200"
                whileHover={{ backgroundColor: "rgba(51, 65, 85, 0.2)" }}
              >
                <span className="text-sm sm:text-base lg:text-lg font-semibold text-white pr-4">{faq.question}</span>
                <motion.svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  animate={{ rotate: openFaq === index ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex-shrink-0 sm:w-6 sm:h-6"
                >
                  <path d="M6 9l6 6 6-6" stroke="#06b6d4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </motion.svg>
              </motion.button>
              
              <motion.div
                initial={false}
                animate={{
                  height: openFaq === index ? "auto" : 0,
                  opacity: openFaq === index ? 1 : 0
                }}
                transition={{ duration: 0.2, ease: "easeInOut" }}
                className="overflow-hidden"
              >
                <div className="px-4 sm:px-6 lg:px-8 pb-4 sm:pb-6 text-slate-300 leading-relaxed text-sm sm:text-base">
                  {faq.answer}
                </div>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default FAQSection;