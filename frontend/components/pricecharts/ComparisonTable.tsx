"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

const ComparisonTable = () => {
  // Features data for comparison table
  const features = [
    "Basic Trading Algorithms",
    "Real-time Market Data",
    "Portfolio Management",
    "Risk Management Tools",
    "Email Notifications",
    "Technical Analysis",
    "Advanced Strategies",
    "API Integration",
    "Priority Support",
    "Custom Indicators",
    "Backtesting Tools",
    "Multi-Exchange Support"
  ];

  // Feature availability by plan
  const planFeatures = {
    Free: [true, true, true, true, true, true, false, false, false, false, false, false],
    Professional: [true, true, true, true, true, true, true, true, false, false, false, false],
    Enterprise: [true, true, true, true, true, true, true, true, true, true, true, true]
  };

  const tableVariants = {
    hidden: { opacity: 0, scale: 0.98 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: "easeOut"
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

  return (
    <motion.div
      variants={tableVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="mb-10 sm:mb-16 md:mb-20"
    >
      <motion.h2
        variants={itemVariants}
        className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-center text-white mb-6 sm:mb-8 md:mb-12 px-4"
      >
        Bot Prices And Comparisons
      </motion.h2>

      {/* Mobile View - Cards */}
      <div className="block lg:hidden space-y-4 sm:space-y-6">
        {['Free', 'Professional', 'Enterprise'].map((plan, planIndex) => (
          <motion.div
            key={plan}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: planIndex * 0.1, duration: 0.3 }}
            className={`bg-slate-800/40 backdrop-blur-sm border rounded-xl p-4 sm:p-6 ${
              plan === 'Professional' 
                ? 'border-blue-500/50 bg-blue-500/5' 
                : 'border-blue-500/20'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className={`font-semibold text-lg sm:text-xl ${
                plan === 'Professional' ? 'text-blue-400' : 'text-white'
              }`}>
                {plan}
              </h3>
              {plan === 'Professional' && (
                <motion.div
                  animate={{ pulse: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="text-xs bg-blue-500 text-white px-2 py-1 rounded-full"
                >
                  Popular
                </motion.div>
              )}
            </div>
            
            <div className="space-y-2 sm:space-y-3">
              {features.map((feature, index) => {
                const hasFeature = planFeatures[plan as keyof typeof planFeatures][index];
                return (
                  <div key={feature} className="flex items-center justify-between">
                    <span className="text-slate-300 text-sm sm:text-base">{feature}</span>
                    {hasFeature ? (
                      <motion.div
                        whileHover={{ scale: 1.2, rotate: 180 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Check size={16} className={`${
                          plan === 'Free' ? 'text-green-500' :
                          plan === 'Professional' ? 'text-blue-500' : 'text-cyan-500'
                        } sm:w-5 sm:h-5`} />
                      </motion.div>
                    ) : (
                      <div className="w-4 h-4 sm:w-5 sm:h-5 bg-slate-600 rounded-full" />
                    )}
                  </div>
                );
              })}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Desktop View - Table */}
      <div className="hidden lg:block bg-slate-800/40 backdrop-blur-sm border border-blue-500/20 rounded-2xl overflow-hidden shadow-2xl shadow-blue-500/10">
        {/* Table Header */}
        <div className="grid grid-cols-4 bg-slate-800/60 border-b border-blue-500/20">
          <div className="p-4 xl:p-6 text-left">
            <h3 className="text-white font-semibold text-base xl:text-lg">Features</h3>
          </div>
          <div className="p-4 xl:p-6 text-center border-l border-blue-500/20">
            <motion.h3
              whileHover={{ scale: 1.05 }}
              className="text-white font-semibold text-base xl:text-lg"
            >
              Free
            </motion.h3>
          </div>
          <div className="p-4 xl:p-6 text-center border-l border-blue-500/20 bg-blue-500/10">
            <motion.h3
              whileHover={{ scale: 1.05 }}
              className="text-blue-400 font-semibold text-base xl:text-lg"
            >
              Professional
            </motion.h3>
            <motion.div
              animate={{ pulse: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="mt-1 text-xs bg-blue-500 text-white px-2 py-1 rounded-full inline-block"
            >
              Popular
            </motion.div>
          </div>
          <div className="p-4 xl:p-6 text-center border-l border-blue-500/20">
            <motion.h3
              whileHover={{ scale: 1.05 }}
              className="text-white font-semibold text-base xl:text-lg"
            >
              Enterprise
            </motion.h3>
          </div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-slate-700/50">
          {features.map((feature, index) => (
            <motion.div
              key={feature}
              initial={{ opacity: 0, x: -10 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
              className="grid grid-cols-4 hover:bg-slate-700/30 transition-colors duration-200"
            >
              <div className="p-3 xl:p-6 text-slate-300">
                <span className="text-sm xl:text-base">{feature}</span>
              </div>
              
              {/* Free Plan */}
              <div className="p-3 xl:p-6 text-center border-l border-blue-500/10">
                {planFeatures.Free[index] ? (
                  <motion.div
                    whileHover={{ scale: 1.2, rotate: 180 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Check size={18} className="text-green-500 mx-auto xl:w-5 xl:h-5" />
                  </motion.div>
                ) : (
                  <div className="w-4 h-4 xl:w-5 xl:h-5 mx-auto bg-slate-600 rounded-full" />
                )}
              </div>
              
              {/* Professional Plan */}
              <div className="p-3 xl:p-6 text-center border-l border-blue-500/10 bg-blue-500/5">
                {planFeatures.Professional[index] ? (
                  <motion.div
                    whileHover={{ scale: 1.2, rotate: 180 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Check size={18} className="text-blue-500 mx-auto xl:w-5 xl:h-5" />
                  </motion.div>
                ) : (
                  <div className="w-4 h-4 xl:w-5 xl:h-5 mx-auto bg-slate-600 rounded-full" />
                )}
              </div>
              
              {/* Enterprise Plan */}
              <div className="p-3 xl:p-6 text-center border-l border-blue-500/10">
                {planFeatures.Enterprise[index] ? (
                  <motion.div
                    whileHover={{ scale: 1.2, rotate: 180 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Check size={18} className="text-cyan-500 mx-auto xl:w-5 xl:h-5" />
                  </motion.div>
                ) : (
                  <div className="w-4 h-4 xl:w-5 xl:h-5 mx-auto bg-slate-600 rounded-full" />
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default ComparisonTable;