"use client"

import { useState, useEffect, useRef } from "react"
import Image from "next/image"
import { ArrowRight, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"

export default function HeroSection() {
  const [scrollY, setScrollY] = useState(0)
  const heroRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const scrollToNextSection = () => {
    const nextSection = heroRef.current?.nextElementSibling
    if (nextSection) {
      nextSection.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <section ref={heroRef} className="relative min-h-screen flex items-center pt-20 overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-background to-background"></div>

        {/* Animated grid */}
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
            transform: `translateY(${scrollY * 0.1}px)`,
            transition: "transform 0.1s ease-out",
          }}
        ></div>

        {/* Floating elements */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-blue-500/10 blur-3xl floating"></div>
        <div
          className="absolute bottom-1/3 right-1/4 w-80 h-80 rounded-full bg-green-500/10 blur-3xl floating"
          style={{ animationDelay: "1s" }}
        ></div>
        <div
          className="absolute top-1/2 right-1/3 w-40 h-40 rounded-full bg-purple-500/10 blur-3xl floating"
          style={{ animationDelay: "2s" }}
        ></div>
      </div>

      <div className="container relative z-10 mx-auto px-4 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
            <div className="flex items-center gap-2 mb-6 bg-white/5 backdrop-blur-sm rounded-full px-4 py-2 w-fit">
              <span className="inline-block w-2 h-2 rounded-full bg-green-400 pulse"></span>
              <span className="text-sm font-medium">Revolutionary AI Technology</span>
            </div>

            <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold mb-6 leading-tight">
              <span className="gradient-text">Forecasting</span> a
              <br />
              Greener Future
            </h1>

            <p className="text-xl text-gray-300 mb-8 max-w-xl">
              Our AI-driven forecasting system predicts solar and wind energy generation with unprecedented accuracy,
              empowering energy companies with actionable insights.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="animated-gradient-bg hover:opacity-90 text-white font-medium">
                Request Demo <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="gradient-border bg-background/50 backdrop-blur-sm hover:bg-background/80"
              >
                Learn More
              </Button>
            </div>

            <div className="mt-12 flex items-center gap-8">
              <div className="flex -space-x-2">
                <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                  A
                </div>
                <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white font-bold">
                  B
                </div>
                <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center text-white font-bold">
                  C
                </div>
                <div className="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center text-white font-bold">
                  D
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-300">Trusted by leading energy companies</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="hidden lg:block"
          >
            <div className="relative">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-green-400 to-blue-500 rounded-2xl blur opacity-30"></div>
              <div className="relative bg-card/50 backdrop-blur-sm border border-white/10 rounded-2xl p-6 shadow-xl">
                <div className="aspect-square relative rounded-xl overflow-hidden mb-6">
                  <Image
                    src="/placeholder.svg?height=600&width=600"
                    alt="Energy forecast visualization"
                    width={600}
                    height={600}
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Solar Forecast</p>
                    <p className="text-2xl font-bold gradient-text">95% Accuracy</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Wind Forecast</p>
                    <p className="text-2xl font-bold gradient-text">92% Accuracy</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <button
        onClick={scrollToNextSection}
        className="absolute bottom-10 left-1/2 transform -translate-x-1/2 flex flex-col items-center gap-2 text-gray-400 hover:text-white transition-colors"
      >
        <span className="text-sm">Scroll to explore</span>
        <ChevronDown className="h-5 w-5 animate-bounce" />
      </button>
    </section>
  )
}

