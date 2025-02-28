"use client"

import { motion } from "framer-motion"
import Image from "next/image"
import { Wind, Sun, Cloud, BarChart2, Zap, Globe } from "lucide-react"

export default function FeaturesSection() {
  const features = [
    {
      icon: <BarChart2 className="h-10 w-10 text-blue-400" />,
      title: "Predictive Analytics",
      description: "Advanced algorithms analyze patterns to forecast energy generation with up to 95% accuracy.",
      image: "/placeholder.svg?height=400&width=600",
      color: "from-blue-500/20 to-transparent",
    },
    {
      icon: <Sun className="h-10 w-10 text-amber-400" />,
      title: "Solar Forecasting",
      description: "Predict solar energy output based on weather patterns, cloud cover, and historical data.",
      image: "/placeholder.svg?height=400&width=600",
      color: "from-amber-500/20 to-transparent",
    },
    {
      icon: <Wind className="h-10 w-10 text-green-400" />,
      title: "Wind Forecasting",
      description: "Accurate wind energy predictions using turbulence models and local terrain analysis.",
      image: "/placeholder.svg?height=400&width=600",
      color: "from-green-500/20 to-transparent",
    },
    {
      icon: <Cloud className="h-10 w-10 text-sky-400" />,
      title: "Weather Integration",
      description: "Real-time weather data integration for continuously updated forecasts.",
      image: "/placeholder.svg?height=400&width=600",
      color: "from-sky-500/20 to-transparent",
    },
    {
      icon: <Zap className="h-10 w-10 text-yellow-400" />,
      title: "Grid Optimization",
      description: "Optimize grid operations with precise generation forecasts to reduce costs and improve stability.",
      image: "/placeholder.svg?height=400&width=600",
      color: "from-yellow-500/20 to-transparent",
    },
    {
      icon: <Globe className="h-10 w-10 text-emerald-400" />,
      title: "Geographic Adaptability",
      description: "Location-specific forecasts that account for local climate and geographical factors.",
      image: "/placeholder.svg?height=400&width=600",
      color: "from-emerald-500/20 to-transparent",
    },
  ]

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  }

  return (
    <section id="features" className="w-full py-20 relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-green-900/10 via-background to-background"></div>

      <div className="container relative z-10 mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full bg-white/5 backdrop-blur-sm">
            <span className="text-sm font-medium gradient-text">Core Features</span>
          </div>
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl mb-4">
            Powering the Future with <span className="gradient-text">Intelligent Forecasting</span>
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Our platform combines cutting-edge AI with comprehensive weather data to revolutionize renewable energy
            forecasting.
          </p>
        </motion.div>

        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={item}
              className="group relative overflow-hidden glass-effect rounded-xl border border-white/5 hover:border-white/10 transition-all duration-500"
            >
              {/* Background Image with Gradient Overlay */}
              <div className="absolute inset-0 transition-transform duration-500 group-hover:scale-110">
                <Image
                  src={feature.image || "/placeholder.svg"}
                  alt={feature.title}
                  fill
                  className="object-cover opacity-20"
                />
                <div className={`absolute inset-0 bg-gradient-to-b ${feature.color}`}></div>
              </div>

              {/* Content */}
              <div className="relative z-10 p-6">
                <div className="flex flex-col h-full">
                  {/* Icon with animated background */}
                  <div className="mb-4 relative">
                    <div className="w-16 h-16 rounded-lg bg-white/5 backdrop-blur-sm flex items-center justify-center transition-transform duration-500 group-hover:scale-110">
                      {feature.icon}
                      <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    </div>
                  </div>

                  {/* Text content with hover effects */}
                  <h3 className="text-xl font-semibold mb-2 transition-colors duration-300 group-hover:text-white">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 transition-colors duration-300 group-hover:text-gray-300">
                    {feature.description}
                  </p>

                  {/* Animated arrow on hover */}
                  <div className="mt-4 flex items-center text-gray-400 transition-colors duration-300 group-hover:text-white">
                    <span className="text-sm font-medium">Learn more</span>
                    <svg
                      className="w-4 h-4 ml-2 transition-transform duration-300 transform group-hover:translate-x-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>

                  {/* Hover gradient border effect */}
                  <div className="absolute inset-0 border border-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-white/20 to-transparent rounded-xl pointer-events-none"></div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

