import React from 'react';
import { motion } from 'framer-motion';

const BotCard = ({ bot, index }) => {
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
        duration: 0.4,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      whileHover={{ 
        scale: 1.02,
        y: -6,
        transition: { duration: 0.2 }
      }}
      className="group relative"
      layout
    >
      {/* Glowing background effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 rounded-xl sm:rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        whileHover={{ scale: 1.03 }}
        transition={{ duration: 0.2 }}
      />
      
      {/* Status badge */}
      <div className="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 z-10">
        <span className={`px-2 sm:px-3 py-1 rounded-full text-xs font-semibold ${
          bot.status === 'Active' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
          bot.status === 'Beta' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
          'bg-purple-500/20 text-purple-400 border border-purple-500/30'
        }`}>
          {bot.status}
        </span>
      </div>
      
      {/* Card content */}
      <div className="relative bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl sm:rounded-2xl p-4 sm:p-6 lg:p-8 h-full group-hover:border-blue-500/30 transition-all duration-300">
        {/* Icon and performance */}
        <div className="flex items-start justify-between mb-4 sm:mb-6">
          <motion.div
            whileHover={{ scale: 1.08, rotateY: 3 }}
            transition={{ duration: 0.2 }}
          >
            <div className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 bg-slate-700/50 rounded-lg sm:rounded-xl flex items-center justify-center group-hover:bg-slate-600/50 transition-colors duration-200">
              <motion.div
                animate={{ 
                  rotateZ: [0, 3, -3, 0],
                }}
                transition={{ 
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12"
              >
                {React.cloneElement(bot.icon, {
                  width: "100%",
                  height: "100%",
                  className: "w-full h-full"
                })}
              </motion.div>
            </div>
          </motion.div>
          
          <div className="text-right">
            <p className="text-xs text-slate-400 mb-1">Performance</p>
            <p className="text-base sm:text-lg font-bold text-green-400">{bot.performance}</p>
          </div>
        </div>

        {/* Category tag */}
        <div className="mb-3 sm:mb-4">
          <span className="px-2 sm:px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full text-xs font-medium border border-blue-500/20">
            {bot.category}
          </span>
        </div>

        {/* Bot name */}
        <motion.h3
          className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-3 sm:mb-4 group-hover:text-blue-300 transition-colors duration-200 leading-tight"
          whileHover={{ x: 3 }}
          transition={{ duration: 0.15 }}
        >
          {bot.name}
        </motion.h3>

        {/* Description */}
        <motion.p
          className="text-slate-400 leading-relaxed text-sm lg:text-base mb-4 sm:mb-6 group-hover:text-slate-300 transition-colors duration-200 line-clamp-3"
          initial={{ opacity: 0.8 }}
          whileHover={{ opacity: 1 }}
        >
          {bot.description}
        </motion.p>

        {/* Action button */}
        <motion.button
          className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg sm:rounded-xl transition-all duration-200 group-hover:shadow-lg group-hover:shadow-blue-500/25 text-sm sm:text-base"
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.15 }}
        >
          Configure Bot
        </motion.button>

        {/* Bottom accent line */}
        <motion.div
          className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500/50 to-cyan-500/50 rounded-full"
          initial={{ scaleX: 0.3, opacity: 0.5 }}
          whileHover={{ scaleX: 1, opacity: 1 }}
          transition={{ duration: 0.2 }}
        />

        {/* Decorative elements */}
        <motion.div
          className="absolute top-3 sm:top-4 right-12 sm:right-16 w-1.5 h-1.5 sm:w-2 sm:h-2 bg-blue-500/40 rounded-full"
          animate={{ 
            scale: [1, 1.4, 1],
            opacity: [0.4, 0.8, 0.4]
          }}
          transition={{ 
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: index * 0.15
          }}
        />
      </div>
    </motion.div>
  );
};

export default BotCard;