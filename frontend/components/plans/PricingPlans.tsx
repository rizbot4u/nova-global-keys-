"use client";

import React from 'react';
import { motion } from 'framer-motion';

interface PricingPlansProps {
  billingCycle: 'monthly' | 'yearly';
}

const PricingPlans = ({ billingCycle }: PricingPlansProps) => {
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

  const cardVariants = {
    hidden: { 
      y: 30,
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

  // Pricing plans data
  const plans = [
    {
      name: "Starter",
      description: "Perfect for beginners exploring AI trading",
      monthlyPrice: 29,
      yearlyPrice: 290,
      popular: false,
      features: [
        "2 DCA Bots included",
        "Basic trading strategies",
        "Email support",
        "Community access",
        "Trade up to $5,000",
        "Basic analytics",
        "Mobile app access"
      ],
      bots: ["DCA Bot", "Basic DC Bot"],
      color: "from-slate-600 to-slate-700",
      borderColor: "border-slate-600/30",
      buttonStyle: "bg-slate-600 hover:bg-slate-700"
    },
    {
      name: "Professional",
      description: "Advanced features for serious traders",
      monthlyPrice: 79,
      yearlyPrice: 790,
      popular: true,
      features: [
        "5 Advanced Bots included",
        "Advanced trading algorithms",
        "Priority support",
        "Expert community access",
        "Trade up to $50,000",
        "Advanced analytics & reports",
        "API integration",
        "Custom strategies"
      ],
      bots: ["All DCA Bots", "Advanced DC Bots", "Strategy Bot"],
      color: "from-blue-600 to-cyan-600",
      borderColor: "border-blue-500/50",
      buttonStyle: "bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500"
    },
    {
      name: "Enterprise",
      description: "Complete solution for professional traders",
      monthlyPrice: 199,
      yearlyPrice: 1990,
      popular: false,
      features: [
        "All 8 Bots included",
        "Custom bot development",
        "24/7 dedicated support",
        "Private community",
        "Unlimited trading volume",
        "Real-time analytics",
        "API & webhook integration",
        "White-label solutions",
        "Risk management tools"
      ],
      bots: ["All Available Bots", "Custom Bots", "Exclusive Features"],
      color: "from-purple-600 to-pink-600",
      borderColor: "border-purple-500/30",
      buttonStyle: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500"
    }
  ];

  // Bot icons for features
  const botIcons = {
    "DCA Bot": (
      <svg width="16" height="16" viewBox="0 0 48 48" fill="none" className="sm:w-5 sm:h-5">
        <rect x="6" y="8" width="36" height="32" rx="4" stroke="#06b6d4" strokeWidth="2" fill="none"/>
        <rect x="10" y="12" width="28" height="20" rx="2" fill="#06b6d4" fillOpacity="0.1"/>
        <circle cx="16" cy="18" r="2" fill="#06b6d4"/>
        <circle cx="24" cy="18" r="2" fill="#06b6d4"/>
      </svg>
    ),
    "DC Bot": (
      <svg width="16" height="16" viewBox="0 0 48 48" fill="none" className="sm:w-5 sm:h-5">
        <circle cx="24" cy="24" r="18" stroke="#06b6d4" strokeWidth="2" fill="none"/>
        <circle cx="24" cy="24" r="12" fill="#06b6d4" fillOpacity="0.1"/>
        <path d="M24 12v24M12 24h24" stroke="#3b82f6" strokeWidth="2"/>
      </svg>
    )
  };

  return (
    <section className="relative py-10 sm:py-16 md:py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8"
        >
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              variants={cardVariants}
              whileHover={{ 
                y: -5,
                scale: 1.02,
                transition: { duration: 0.2 }
              }}
              className={`relative group ${plan.popular ? 'lg:scale-105' : ''} ${
                plan.popular ? 'order-first lg:order-none' : ''
              }`}
            >
              {/* Popular badge */}
              {plan.popular && (
                <motion.div
                  initial={{ scale: 0, opacity: 0 }}
                  whileInView={{ scale: 1, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                  className="absolute -top-3 sm:-top-4 left-1/2 transform -translate-x-1/2 z-10"
                >
                  <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-3 sm:px-6 py-1 sm:py-2 rounded-full text-xs sm:text-sm font-bold shadow-lg">
                    Most Popular
                  </div>
                </motion.div>
              )}

              {/* Glowing background */}
              <motion.div
                className={`absolute inset-0 bg-gradient-to-br ${plan.color} rounded-2xl sm:rounded-3xl blur-xl opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
                whileHover={{ scale: 1.05 }}
              />

              {/* Card content */}
              <div className={`relative bg-slate-800/50 backdrop-blur-sm border ${plan.borderColor} rounded-2xl sm:rounded-3xl p-4 sm:p-6 lg:p-8 h-full group-hover:border-opacity-70 transition-all duration-300`}>
                {/* Plan header */}
                <div className="text-center mb-6 sm:mb-8">
                  <h3 className="text-xl sm:text-2xl font-bold text-white mb-1 sm:mb-2">{plan.name}</h3>
                  <p className="text-slate-400 text-sm sm:text-base mb-4 sm:mb-6">{plan.description}</p>
                  
                  {/* Price */}
                  <div className="mb-4 sm:mb-6">
                    <motion.div
                      key={billingCycle}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.2 }}
                      className="flex items-baseline justify-center"
                    >
                      <span className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
                        ${billingCycle === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice}
                      </span>
                      <span className="text-slate-400 ml-1 sm:ml-2 text-sm sm:text-base">
                        /{billingCycle === 'monthly' ? 'month' : 'year'}
                      </span>
                    </motion.div>
                    {billingCycle === 'yearly' && (
                      <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.2 }}
                        className="text-green-400 text-xs sm:text-sm mt-1 sm:mt-2"
                      >
                        Save ${(plan.monthlyPrice * 12) - plan.yearlyPrice} per year
                      </motion.p>
                    )}
                  </div>

                  {/* CTA Button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full ${plan.buttonStyle} text-white px-4 sm:px-6 lg:px-8 py-3 sm:py-4 rounded-lg sm:rounded-xl font-semibold text-sm sm:text-base lg:text-lg transition-all duration-200 shadow-lg mb-6 sm:mb-8`}
                  >
                    {plan.name === 'Enterprise' ? 'Contact Sales' : 'Start Free Trial'}
                  </motion.button>
                </div>

                {/* Features */}
                <div className="space-y-2 sm:space-y-4">
                  <h4 className="text-base sm:text-lg font-semibold text-white mb-2 sm:mb-4">Features included:</h4>
                  {plan.features.map((feature, featureIndex) => (
                    <motion.div
                      key={featureIndex}
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.2, delay: featureIndex * 0.05 }}
                      className="flex items-center space-x-2 sm:space-x-3"
                    >
                      <div className="w-4 h-4 sm:w-5 sm:h-5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg width="8" height="8" viewBox="0 0 12 12" fill="none" className="sm:w-3 sm:h-3">
                          <path d="M2 6L5 9L10 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <span className="text-slate-300 text-sm sm:text-base">{feature}</span>
                    </motion.div>
                  ))}
                </div>

                {/* Included Bots */}
                <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-slate-700/50">
                  <h4 className="text-base sm:text-lg font-semibold text-white mb-2 sm:mb-4">Included Bots:</h4>
                  <div className="space-y-1 sm:space-y-2">
                    {plan.bots.map((bot, botIndex) => (
                      <motion.div
                        key={botIndex}
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.2, delay: botIndex * 0.05 }}
                        className="flex items-center space-x-2 sm:space-x-3"
                      >
                        <div className="w-6 h-6 sm:w-8 sm:h-8 bg-slate-700/50 rounded-md sm:rounded-lg flex items-center justify-center flex-shrink-0">
                          {botIcons[bot as keyof typeof botIcons] || (
                            <div className="w-2 h-2 sm:w-3 sm:h-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full" />
                          )}
                        </div>
                        <span className="text-blue-300 font-medium text-sm sm:text-base">{bot}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default PricingPlans;