"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { FileText, TrendingUp, AlertCircle, Users, CreditCard, Scale, Ban, CheckCircle } from 'lucide-react';

const TermsOfServiceSection = () => {
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
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
        duration: 0.6,
        ease: "easeOut"
      }
    }
  };

  const iconVariants = {
    hidden: { scale: 0, rotate: -180 },
    visible: {
      scale: 1,
      rotate: 0,
      transition: {
        duration: 0.8,
        ease: "easeOut"
      }
    }
  };

  const terms = [
    {
      icon: CheckCircle,
      title: "Acceptance of Terms",
      content: "By accessing and using our crypto trading bot platform, you agree to comply with these Terms of Service. If you disagree with any part of these terms, you may not use our services. These terms apply to all users, including visitors and registered members."
    },
    {
      icon: TrendingUp,
      title: "Trading Bot Services",
      content: "Our platform provides automated crypto trading bots that execute trades based on your configured strategies. You acknowledge that crypto trading is highly volatile and risky. Our bots are tools to assist your trading decisions, but all trading risks remain with you."
    },
    {
      icon: Users,
      title: "User Responsibilities",
      content: "You must provide accurate information, maintain the security of your account, and comply with all applicable laws. You're responsible for all activities under your account and must not use our service for illegal activities or market manipulation."
    },
    {
      icon: CreditCard,
      title: "Fees and Payments",
      content: "Subscription fees are billed in advance and are non-refundable except as required by law. We may change our pricing with 30 days notice. Additional fees may apply for premium features, high-frequency trading, or API usage beyond standard limits."
    },
    {
      icon: AlertCircle,
      title: "Risk Disclosure",
      content: "Cryptocurrency trading involves substantial risk of loss. Past performance doesn't guarantee future results. Our bots may malfunction, markets may be volatile, and you could lose your entire investment. Only trade with funds you can afford to lose."
    },
    {
      icon: Ban,
      title: "Prohibited Activities",
      content: "You may not reverse engineer our software, manipulate markets, use our service for money laundering, share your account, or attempt to gain unauthorized access to our systems. Violations may result in immediate account termination."
    },
    {
      icon: Scale,
      title: "Limitation of Liability",
      content: "We're not liable for trading losses, market volatility, exchange failures, or technical issues. Our liability is limited to the amount you paid for our services. We provide the platform 'as-is' without warranties of profitability or performance."
    },
    {
      icon: FileText,
      title: "Intellectual Property",
      content: "Our trading algorithms, software, and content are proprietary. You receive a limited license to use our services but may not copy, distribute, or create derivative works. All trademarks and copyrights remain our property."
    }
  ];

  const highlights = [
    "18+ years old required",
    "KYC verification may be required",
    "Not available in restricted jurisdictions",
    "Account termination for violations",
    "30-day notice for terms changes",
    "Disputes resolved through arbitration"
  ];

  return (
    <div className="relative bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 py-20 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 30% 20%, rgba(239, 68, 68, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 70% 80%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 20% 70%, rgba(16, 185, 129, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px, 80px 80px, 40px 40px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6">
        {/* Header Section */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="text-center mb-16"
        >
          <motion.div
            variants={iconVariants}
            className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl mb-6"
          >
            <Scale className="w-10 h-10 text-white" />
          </motion.div>

          <motion.h1
            variants={itemVariants}
            className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight"
          >
            Terms of Service
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed"
          >
            Please read these terms carefully before using our crypto trading bot platform. These terms govern your use of our services and protect both parties.
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="mt-8 inline-flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700"
          >
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-slate-400">Effective: January 2025</span>
          </motion.div>
        </motion.div>

        {/* Key Highlights */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="mb-16"
        >
          <motion.h2
            variants={itemVariants}
            className="text-3xl font-bold text-white mb-8 text-center"
          >
            Key Points
          </motion.h2>
          
          <motion.div
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {highlights.map((highlight, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-4 text-center"
              >
                <span className="text-slate-300 font-medium">{highlight}</span>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Terms Sections */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16"
        >
          {terms.map((term, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ 
                scale: 1.02,
                boxShadow: "0 10px 40px rgba(239, 68, 68, 0.1)"
              }}
              className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 hover:border-red-500/30 transition-all duration-300"
            >
              <motion.div
                variants={iconVariants}
                className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-xl mb-6"
              >
                <term.icon className="w-7 h-7 text-red-400" />
              </motion.div>

              <motion.h3
                variants={itemVariants}
                className="text-2xl font-bold text-white mb-4"
              >
                {term.title}
              </motion.h3>

              <motion.p
                variants={itemVariants}
                className="text-slate-300 leading-relaxed text-lg"
              >
                {term.content}
              </motion.p>
            </motion.div>
          ))}
        </motion.div>

        {/* Warning Section */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="mb-16 bg-gradient-to-r from-yellow-500/10 to-red-500/10 rounded-3xl border border-yellow-500/20 p-12"
        >
          <motion.div
            variants={iconVariants}
            className="flex justify-center mb-6"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-500/20 rounded-full">
              <AlertCircle className="w-8 h-8 text-yellow-400" />
            </div>
          </motion.div>

          <motion.h2
            variants={itemVariants}
            className="text-3xl font-bold text-white mb-4 text-center"
          >
            Important Risk Warning
          </motion.h2>
          
          <motion.p
            variants={itemVariants}
            className="text-slate-300 text-lg text-center max-w-4xl mx-auto leading-relaxed"
          >
            Cryptocurrency trading carries significant financial risk. Our automated trading bots are sophisticated tools, but they cannot eliminate market risk or guarantee profits. 
            You could lose some or all of your invested capital. Only use funds you can afford to lose, and never invest borrowed money. 
            Past performance does not indicate future results. Always conduct your own research and consider seeking advice from qualified financial advisors.
          </motion.p>
        </motion.div>

        {/* Contact Section */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="text-center bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-3xl border border-blue-500/20 p-12"
        >
          <motion.h2
            variants={itemVariants}
            className="text-3xl font-bold text-white mb-4"
          >
            Questions About These Terms?
          </motion.h2>
          
          <motion.p
            variants={itemVariants}
            className="text-slate-300 text-lg mb-8 max-w-2xl mx-auto"
          >
            Our legal team is available to clarify any aspects of these terms. We're committed to maintaining transparent and fair business practices.
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <motion.button
              whileHover={{ 
                scale: 1.05,
                boxShadow: "0 20px 40px rgba(59, 130, 246, 0.3)"
              }}
              whileTap={{ scale: 0.98 }}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 shadow-lg shadow-blue-500/25"
            >
              Contact Legal Team
            </motion.button>

            <motion.button
              whileHover={{ 
                scale: 1.05,
                borderColor: "rgb(59 130 246)"
              }}
              whileTap={{ scale: 0.98 }}
              className="border-2 border-slate-600 hover:border-blue-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300"
            >
              Download PDF
            </motion.button>
          </motion.div>

          <motion.p
            variants={itemVariants}
            className="text-slate-400 text-sm mt-6"
          >
            By continuing to use our services, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
};

export default TermsOfServiceSection;