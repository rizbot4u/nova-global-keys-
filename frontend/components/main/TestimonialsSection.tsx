"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Star } from 'lucide-react';

const TestimonialsSection = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  // Testimonials data
  const testimonials = [
    {
      id: 1,
      name: "John Smith",
      role: "User",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face",
      rating: 5,
      text: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim mi turpis etiam faucibus felis condimentum amet placerat duis tellus variu. Lorem ipsum dolor sit amet consectetur adipiscing"
    },
    {
      id: 2,
      name: "Mickael Grants",
      role: "CEO",
      avatar: "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&h=100&fit=crop&crop=face",
      rating: 5,
      text: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim mi turpis etiam faucibus felis condimentum amet placerat duis tellus variu. Lorem ipsum dolor sit amet consectetur adipiscing"
    },
    {
      id: 3,
      name: "John Smith",
      role: "User",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
      rating: 5,
      text: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim mi turpis etiam faucibus felis condimentum amet placerat duis tellus variu. Lorem ipsum dolor sit amet consectetur adipiscing"
    },
    {
      id: 4,
      name: "Sarah Johnson",
      role: "Trader",
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face",
      rating: 5,
      text: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim mi turpis etiam faucibus felis condimentum amet placerat duis tellus variu. Lorem ipsum dolor sit amet consectetur adipiscing"
    },
    {
      id: 5,
      name: "David Chen",
      role: "Investor",
      avatar: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=100&h=100&fit=crop&crop=face",
      rating: 5,
      text: "Lorem ipsum dolor sit amet consectetur adipiscing elit et ac adipiscing quis enim mi turpis etiam faucibus felis condimentum amet placerat duis tellus variu. Lorem ipsum dolor sit amet consectetur adipiscing"
    }
  ];

  // Auto-play functionality
  useEffect(() => {
    if (!isAutoPlaying) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [isAutoPlaying, testimonials.length]);

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    setIsAutoPlaying(false);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
    setIsAutoPlaying(false);
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
    setIsAutoPlaying(false);
  };

  // Get visible testimonials (current and adjacent)
  const getVisibleTestimonials = () => {
    const visible = [];
    for (let i = -1; i <= 1; i++) {
      const index = (currentIndex + i + testimonials.length) % testimonials.length;
      visible.push({
        ...testimonials[index],
        position: i
      });
    }
    return visible;
  };

  // Animation variants - faster and smoother
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.05
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
        duration: 0.5,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const cardVariants = {
    hidden: { scale: 0.9, opacity: 0 },
    visible: { scale: 1, opacity: 1 },
    exit: { scale: 0.9, opacity: 0 }
  };

  const TestimonialCard = ({ testimonial, position }: { testimonial: any; position: number }) => {
    const isCenter = position === 0;
    const isLeft = position === -1;
    const isRight = position === 1;

    return (
      <motion.div
        layout
        initial={cardVariants.hidden}
        animate={cardVariants.visible}
        exit={cardVariants.exit}
        transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
        className={`relative flex-shrink-0 transition-all duration-300 ${
          isCenter 
            ? 'w-full sm:w-80 md:w-96 scale-100 z-20' 
            : 'hidden md:block w-64 lg:w-80 scale-90 opacity-50 z-10'
        } ${isLeft ? 'md:-translate-x-4 lg:-translate-x-8' : ''} ${isRight ? 'md:translate-x-4 lg:translate-x-8' : ''}`}
        style={{ 
          transform: `translateX(${position * (isCenter ? 0 : position > 0 ? 15 : -15)}px) scale(${isCenter ? 1 : 0.9})`,
          filter: isCenter ? 'none' : 'brightness(0.7)'
        }}
      >
        {/* Glowing background effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-xl sm:rounded-2xl blur-xl"
          animate={{ 
            scale: isCenter ? [1, 1.03, 1] : [0.9, 0.93, 0.9],
            opacity: isCenter ? [0.5, 0.8, 0.5] : [0.3, 0.5, 0.3]
          }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        />
        
        {/* Card content */}
        <div className={`relative bg-slate-800/60 backdrop-blur-sm border rounded-xl sm:rounded-2xl p-4 sm:p-6 lg:p-8 h-full transition-all duration-300 ${
          isCenter ? 'border-blue-500/30 shadow-xl shadow-blue-500/10' : 'border-slate-700/50'
        }`}>
          {/* Quote icon */}
          <motion.div
            className="absolute top-3 right-3 sm:top-4 sm:right-4 text-blue-500/30"
            animate={{ rotateY: isCenter ? [0, 180, 0] : 0 }}
            transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
          >
            <svg width="20" height="20" className="sm:w-6 sm:h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-10zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h4v10h-10z"/>
            </svg>
          </motion.div>

          {/* Testimonial text */}
          <motion.p
            className="text-slate-300 leading-relaxed mb-6 sm:mb-8 text-xs sm:text-sm lg:text-base line-clamp-4 sm:line-clamp-none"
            animate={{ opacity: isCenter ? 1 : 0.7 }}
            transition={{ duration: 0.2 }}
          >
            {testimonial.text}
          </motion.p>

          {/* User info and rating */}
          <div className="flex items-center justify-between">
            {/* User info */}
            <div className="flex items-center space-x-3 sm:space-x-4">
              <motion.div
                className="relative"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.15 }}
              >
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-slate-600 overflow-hidden ring-2 ring-blue-500/30">
                  <div className="w-full h-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white font-bold text-sm sm:text-base">
                    {testimonial.name.charAt(0)}
                  </div>
                </div>
                {/* Online indicator for center card */}
                {isCenter && (
                  <motion.div
                    className="absolute -bottom-0.5 -right-0.5 sm:-bottom-1 sm:-right-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-500 rounded-full border-2 border-slate-800"
                    animate={{ scale: [1, 1.15, 1] }}
                    transition={{ duration: 1.8, repeat: Infinity }}
                  />
                )}
              </motion.div>
              
              <div className="min-w-0 flex-1">
                <motion.h4
                  className="text-white font-semibold text-sm sm:text-base lg:text-lg truncate"
                  animate={{ opacity: isCenter ? 1 : 0.8 }}
                >
                  {testimonial.name}
                </motion.h4>
                <motion.p
                  className="text-slate-400 text-xs sm:text-sm truncate"
                  animate={{ opacity: isCenter ? 0.7 : 0.5 }}
                >
                  {testimonial.role}
                </motion.p>
              </div>
            </div>

            {/* Star rating */}
            <motion.div
              className="flex space-x-0.5 sm:space-x-1 flex-shrink-0"
              animate={{ scale: isCenter ? 1 : 0.9 }}
              transition={{ duration: 0.2 }}
            >
              {[...Array(5)].map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ 
                    delay: i * 0.05,
                    duration: 0.3,
                    type: "spring",
                    stiffness: 250
                  }}
                >
                  <Star
                    size={14}
                    className={`sm:w-4 sm:h-4 ${
                      i < testimonial.rating 
                        ? 'fill-yellow-400 text-yellow-400' 
                        : 'text-slate-600'
                    } transition-colors duration-150`}
                  />
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="relative bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 py-12 sm:py-16 md:py-20 lg:py-32 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 75% 75%, rgba(6, 182, 212, 0.1) 1px, transparent 1px),
              radial-gradient(circle at 50% 10%, rgba(59, 130, 246, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px, 50px 50px, 40px 40px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6">
        {/* Section Header */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="text-center mb-10 sm:mb-12 lg:mb-16"
        >
          {/* Section Label */}
          <motion.p
            variants={titleVariants}
            className="text-slate-400 text-sm sm:text-base lg:text-lg font-medium mb-2 sm:mb-4 tracking-wide"
          >
            Client Highlight
          </motion.p>

          {/* Main Heading */}
          <motion.h2
            variants={titleVariants}
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-white leading-tight px-2"
          >
            What Our{" "}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Clients Say
            </span>
          </motion.h2>
        </motion.div>

        {/* Testimonials Carousel */}
        <div className="relative">
          {/* Cards Container */}
          <div className="flex justify-center items-center space-x-2 sm:space-x-4 md:space-x-8 min-h-[320px] sm:min-h-[360px] lg:min-h-[400px] px-2">
            <AnimatePresence mode="wait">
              {getVisibleTestimonials().map((testimonial) => (
                <TestimonialCard
                  key={`${testimonial.id}-${testimonial.position}`}
                  testimonial={testimonial}
                  position={testimonial.position}
                />
              ))}
            </AnimatePresence>
          </div>

          {/* Navigation Controls */}
          <div className="flex justify-center items-center space-x-3 sm:space-x-4 mt-8 sm:mt-10 lg:mt-12">
            {/* Previous Button */}
            <motion.button
              onClick={prevSlide}
              whileHover={{ scale: 1.05, backgroundColor: "rgba(59, 130, 246, 0.2)" }}
              whileTap={{ scale: 0.95 }}
              className="w-10 h-10 sm:w-12 sm:h-12 rounded-full border border-blue-500/30 flex items-center justify-center text-blue-400 hover:border-blue-400/50 transition-all duration-200 backdrop-blur-sm"
            >
              <ChevronLeft size={16} className="sm:w-5 sm:h-5" />
            </motion.button>

            {/* Dots Indicator */}
            <div className="flex space-x-1.5 sm:space-x-2">
              {testimonials.map((_, index) => (
                <motion.button
                  key={index}
                  onClick={() => goToSlide(index)}
                  whileHover={{ scale: 1.15 }}
                  whileTap={{ scale: 0.9 }}
                  className={`w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full transition-all duration-200 ${
                    index === currentIndex
                      ? 'bg-blue-500 shadow-lg shadow-blue-500/50'
                      : 'bg-slate-600 hover:bg-slate-500'
                  }`}
                />
              ))}
            </div>

            {/* Next Button */}
            <motion.button
              onClick={nextSlide}
              whileHover={{ scale: 1.05, backgroundColor: "rgba(59, 130, 246, 0.2)" }}
              whileTap={{ scale: 0.95 }}
              className="w-10 h-10 sm:w-12 sm:h-12 rounded-full border border-blue-500/30 flex items-center justify-center text-blue-400 hover:border-blue-400/50 transition-all duration-200 backdrop-blur-sm"
            >
              <ChevronRight size={16} className="sm:w-5 sm:h-5" />
            </motion.button>
          </div>
        </div>

        {/* Auto-play indicator */}
        <motion.div
          className="flex justify-center mt-6 sm:mt-8"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.8 }}
        >
          <motion.div
            className="flex items-center space-x-2 text-slate-500 text-xs sm:text-sm"
            whileHover={{ scale: 1.03 }}
          >
            <div className={`w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full ${isAutoPlaying ? 'bg-green-500' : 'bg-slate-500'} transition-colors duration-200`} />
            <span>{isAutoPlaying ? 'Auto-playing' : 'Manual control'}</span>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default TestimonialsSection;