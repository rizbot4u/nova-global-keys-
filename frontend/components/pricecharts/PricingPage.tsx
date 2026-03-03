"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import HeroSectionPricing from './HeroSectionPricing';
import ComparisonTable from './ComparisonTable';
import FAQGrid from './FAQGrid';

const PricingPage = () => {
  const [openFAQ, setOpenFAQ] = useState<number | null>(0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-blue-900/20 to-slate-900 relative overflow-hidden">
      {/* Animated Background Pattern */}
      <div className="absolute inset-0 opacity-30">
        <motion.div
          animate={{ 
            backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"]
          }}
          transition={{ 
            duration: 20, 
            repeat: Infinity, 
            ease: "linear" 
          }}
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(45deg, transparent 30%, rgba(59, 130, 246, 0.1) 50%, transparent 70%),
              linear-gradient(-45deg, transparent 30%, rgba(6, 182, 212, 0.1) 50%, transparent 70%),
              radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '200px 200px, 200px 200px, 50px 50px, 60px 60px'
          }}
        />
      </div>

      {/* Glowing orbs */}
      <motion.div
        animate={{ 
          x: [0, 50, 0],
          y: [0, -25, 0],
          scale: [1, 1.2, 1]
        }}
        transition={{ 
          duration: 4, 
          repeat: Infinity, 
          ease: "easeInOut" 
        }}
        className="absolute top-10 sm:top-20 left-5 sm:left-10 w-32 h-32 sm:w-64 sm:h-64 bg-blue-500/10 rounded-full blur-3xl"
      />
      <motion.div
        animate={{ 
          x: [0, -40, 0],
          y: [0, 30, 0],
          scale: [1, 0.8, 1]
        }}
        transition={{ 
          duration: 5, 
          repeat: Infinity, 
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute bottom-10 sm:bottom-20 right-5 sm:right-10 w-40 h-40 sm:w-80 sm:h-80 bg-cyan-500/10 rounded-full blur-3xl"
      />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-10 sm:py-16 md:py-20">
        <HeroSectionPricing />
        <ComparisonTable />
        <FAQGrid openFAQ={openFAQ} setOpenFAQ={setOpenFAQ} />
      </div>
    </div>
  );
};

export default PricingPage;