"use client";

import React from 'react';
import { motion } from 'framer-motion';
import BotCard from './BotCard';
import FilterButtons from './FilterButtons';
import BackgroundPattern from './BackgroundPattern';
import { botsData, categories } from './botsData';

const TradingBotsPage = () => {
  const [activeCategory, setActiveCategory] = React.useState("All");
  const [filteredBots, setFilteredBots] = React.useState(botsData);

  // Filter bots based on active category
  React.useEffect(() => {
    if (activeCategory === "All") {
      setFilteredBots(botsData);
    } else {
      setFilteredBots(botsData.filter(bot => bot.category === activeCategory));
    }
  }, [activeCategory]);

  // Optimized animation variants
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

  const titleVariants = {
    hidden: { 
      y: 30, 
      opacity: 0 
    },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.6,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const filterVariants = {
    hidden: { y: 15, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.4 }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
      <BackgroundPattern />

      <div className="relative z-10">
        {/* Page Header */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-20 lg:pt-24 pb-8 sm:pb-12">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="text-center"
          >
            {/* Page Title */}
            <motion.h1
              variants={titleVariants}
              className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-white leading-tight mb-4 sm:mb-6 px-2"
            >
              AI Trading{" "}
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                Bots
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={titleVariants}
              className="text-base sm:text-lg lg:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed px-4"
            >
              Discover our collection of advanced trading bots designed to maximize your profits 
              with intelligent automation and risk management
            </motion.p>
          </motion.div>
        </div>

        {/* Filter Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8 sm:mb-12">
          <motion.div
            variants={filterVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <FilterButtons 
              categories={categories}
              activeCategory={activeCategory}
              setActiveCategory={setActiveCategory}
            />
          </motion.div>
        </div>

        {/* Bots Grid */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 sm:pb-20">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8"
          >
            {filteredBots.map((bot, index) => (
              <BotCard key={bot.id} bot={bot} index={index} />
            ))}
          </motion.div>

          {/* No results message */}
          {filteredBots.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="text-center py-16 sm:py-20"
            >
              <p className="text-slate-400 text-lg">No bots found in this category</p>
            </motion.div>
          )}
        </div>

        {/* Bottom CTA Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 sm:pb-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-2xl sm:rounded-3xl p-6 sm:p-8 lg:p-12"
          >
            <h3 className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4">
              Need a Custom Trading Bot?
            </h3>
            <p className="text-slate-300 text-base sm:text-lg mb-6 sm:mb-8 max-w-2xl mx-auto px-2">
              Our team can develop personalized trading strategies tailored to your specific needs and risk profile
            </p>
            <motion.button
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold py-3 sm:py-4 px-6 sm:px-8 rounded-xl transition-all duration-200 shadow-lg shadow-blue-500/25"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              transition={{ duration: 0.15 }}
            >
              Contact Our Experts
            </motion.button>
          </motion.div>
        </div>

        {/* Decorative bottom element */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex justify-center pb-8 sm:pb-12"
        >
          <div className="w-16 sm:w-24 h-1 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full opacity-60" />
        </motion.div>
      </div>
    </div>
  );
};

export default TradingBotsPage;