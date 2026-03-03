"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Eye, Lock, Database, UserCheck, AlertTriangle } from 'lucide-react';

// Animation variants - faster and smoother
const fadeInUp = {
  hidden: { 
    y: 20, 
    opacity: 0 
  },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.3,
      ease: [0.25, 0.46, 0.45, 0.94]
    }
  }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.05
    }
  }
};

const scaleIn = {
  hidden: { scale: 0.9, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: 0.25,
      ease: "easeOut"
    }
  }
};

// Header Component
const PrivacyHeader = () => {
  return (
    <motion.header
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="text-center mb-12 sm:mb-16 lg:mb-20 px-4 sm:px-6"
    >
      <motion.div
        variants={scaleIn}
        className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl mb-6"
      >
        <Shield className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
      </motion.div>

      <motion.h1
        variants={fadeInUp}
        className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 sm:mb-6 leading-tight px-2"
      >
        Privacy Policy
      </motion.h1>

      <motion.p
        variants={fadeInUp}
        className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed px-4"
      >
        Your privacy and security are our top priorities. Learn how we protect your data while providing world-class crypto trading automation.
      </motion.p>

      <motion.div
        variants={fadeInUp}
        className="mt-6 sm:mt-8 inline-flex items-center space-x-2 bg-slate-800/50 px-3 py-2 sm:px-4 rounded-full border border-slate-700"
      >
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span className="text-xs sm:text-sm text-slate-400">Last updated: January 2025</span>
      </motion.div>
    </motion.header>
  );
};

// Blog Section Component
const BlogSection = ({ icon: Icon, title, children }) => {
  return (
    <motion.section
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-30px" }}
      className="mb-8 sm:mb-12 lg:mb-16 px-4 sm:px-6"
    >
      <div className="flex flex-col sm:flex-row sm:items-start gap-4 sm:gap-6 max-w-4xl mx-auto">
        <motion.div
          variants={scaleIn}
          whileHover={{ scale: 1.05 }}
          transition={{ duration: 0.15 }}
          className="flex-shrink-0 inline-flex items-center justify-center w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl self-start"
        >
          <Icon className="w-6 h-6 sm:w-7 sm:h-7 text-blue-400" />
        </motion.div>

        <div className="flex-1">
          <motion.h3
            variants={fadeInUp}
            className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mb-3 sm:mb-4"
          >
            {title}
          </motion.h3>

          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="text-slate-300 leading-relaxed text-base sm:text-lg space-y-4"
          >
            {React.Children.map(children, (child, index) => (
              <motion.div key={index} variants={fadeInUp}>
                {child}
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </motion.section>
  );
};

// Contact Section Component
const ContactSection = () => {
  return (
    <motion.section
      variants={staggerContainer}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="mt-12 sm:mt-16 lg:mt-20 px-4 sm:px-6"
    >
      <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 rounded-2xl sm:rounded-3xl border border-blue-500/20 p-6 sm:p-8 lg:p-12 max-w-4xl mx-auto">
        <motion.h2
          variants={fadeInUp}
          className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4 text-center"
        >
          Questions About Your Privacy?
        </motion.h2>
        
        <motion.p
          variants={fadeInUp}
          className="text-slate-300 text-base sm:text-lg mb-6 sm:mb-8 text-center leading-relaxed"
        >
          We're committed to transparency. If you have any questions about how we handle your data or want to exercise your privacy rights, we're here to help.
        </motion.p>

        <motion.div
          variants={fadeInUp}
          className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center"
        >
          <motion.button
            whileHover={{ 
              scale: 1.02,
              boxShadow: "0 8px 25px rgba(59, 130, 246, 0.25)"
            }}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-semibold text-base sm:text-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
          >
            Contact Privacy Team
          </motion.button>

          <motion.button
            whileHover={{ 
              scale: 1.02,
              borderColor: "rgb(59 130 246)"
            }}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="w-full sm:w-auto border-2 border-slate-600 hover:border-blue-500 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-semibold text-base sm:text-lg transition-all duration-200"
          >
            Download Your Data
          </motion.button>
        </motion.div>
      </div>
    </motion.section>
  );
};

// Main Privacy Policy Component
const PrivacyPolicyBlog = () => {
  return (
    <div className="relative bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 py-12 sm:py-16 lg:py-20 overflow-hidden min-h-screen">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 75% 75%, rgba(6, 182, 212, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '30px 30px, 50px 50px, 20px 20px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto">
        <PrivacyHeader />

        <motion.main 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-0"
        >
          <BlogSection icon={Database} title="Information We Collect">
            <p>
              We collect information you provide when creating an account, configuring trading bots, and using our services. This includes email addresses, trading preferences, API keys (which are encrypted), and usage analytics to improve our crypto trading algorithms.
            </p>
            <p>
              Our data collection is transparent and minimal - we only gather what's necessary to provide you with exceptional crypto trading automation services. You have full control over what information you share with us.
            </p>
          </BlogSection>

          <BlogSection icon={Eye} title="How We Use Your Information">
            <p>
              Your data helps us provide personalized crypto trading experiences, optimize bot performance, send important security notifications, and improve our AI algorithms. We never use your trading data for our own benefit or share it with competitors.
            </p>
            <p>
              Every piece of information serves a specific purpose in enhancing your trading experience. We believe in using data responsibly to create better outcomes for our users while maintaining strict ethical standards.
            </p>
          </BlogSection>

          <BlogSection icon={Lock} title="Data Security & Encryption">
            <p>
              All sensitive data, including API keys and trading information, is encrypted using AES-256 encryption. We employ multi-layer security protocols, cold storage for sensitive data, and regular security audits to protect your crypto assets and personal information.
            </p>
            <p>
              Security isn't just a feature for us - it's the foundation of everything we do. Our infrastructure is designed with security-first principles, ensuring your data remains protected against evolving threats in the digital landscape.
            </p>
          </BlogSection>

          <BlogSection icon={UserCheck} title="Third-Party Integrations">
            <p>
              We integrate with major crypto exchanges through secure APIs. We only access the minimum permissions required for trading operations. Exchange API keys are encrypted and never stored in plain text. We don't store your exchange login credentials.
            </p>
            <p>
              Our partnerships with exchanges are built on trust and security. We maintain strict data handling protocols with all third-party services to ensure your information remains protected throughout the entire trading ecosystem.
            </p>
          </BlogSection>

          <BlogSection icon={Shield} title="Your Privacy Rights">
            <p>
              You have the right to access, modify, or delete your personal data. You can export your trading history, disable data collection features, and request complete account deletion. We comply with GDPR, CCPA, and other privacy regulations.
            </p>
            <p>
              Privacy rights aren't just legal requirements - they're fundamental principles we uphold. We provide easy-to-use tools that put you in control of your data, ensuring you can manage your privacy preferences with complete transparency.
            </p>
          </BlogSection>

          <BlogSection icon={AlertTriangle} title="Risk Disclosure">
            <p>
              Crypto trading involves significant financial risk. Our bots use your data to make automated trades based on your configured strategies. Past performance data is used for algorithm improvement but doesn't guarantee future results. Always trade responsibly.
            </p>
            <p>
              We believe in empowering informed decision-making. Understanding the risks involved in crypto trading is essential, and we're committed to providing you with the tools and information needed to make responsible trading choices.
            </p>
          </BlogSection>
        </motion.main>

        <ContactSection />
      </div>
    </div>
  );
};

export default PrivacyPolicyBlog;