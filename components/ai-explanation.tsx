"use client"

import { motion } from "framer-motion"
import Image from "next/image"
import { Brain, Database, Cpu, BarChart2 } from "lucide-react"

export default function AIExplanation() {
  return (
    <section id="technology" className="w-full py-20 relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-900/10 via-background to-background"></div>

      <div className="container relative z-10 mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full bg-white/5 backdrop-blur-sm hover:bg-white/10 transition-colors duration-300">
            <span className="text-sm font-medium gradient-text">Advanced Technology</span>
          </div>
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl mb-4">
            <span className="gradient-text">AI-Powered</span> Prediction Technology
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Our advanced machine learning models analyze vast amounts of data to deliver accurate energy forecasts.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="order-2 lg:order-1"
          >
            <div className="space-y-8">
              <div className="flex gap-6 glass-effect p-6 rounded-xl border border-white/5 transition-all duration-300 hover:border-blue-500/50 hover:shadow-md hover:shadow-blue-500/20 group">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center transition-all duration-300 group-hover:bg-blue-500/30 group-hover:scale-110">
                  <Database className="h-6 w-6 text-blue-400 group-hover:text-blue-300 transition-colors duration-300" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-blue-400 transition-colors duration-300">Historical Data Analysis</h3>
                  <p className="text-gray-400">
                    Our AI analyzes years of historical weather and energy production data to identify patterns and
                    correlations that human analysts might miss.
                  </p>
                </div>
              </div>

              <div className="flex gap-6 glass-effect p-6 rounded-xl border border-white/5 transition-all duration-300 hover:border-green-500/50 hover:shadow-md hover:shadow-green-500/20 group">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center transition-all duration-300 group-hover:bg-green-500/30 group-hover:scale-110">
                  <Brain className="h-6 w-6 text-green-400 group-hover:text-green-300 transition-colors duration-300" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-green-400 transition-colors duration-300">Machine Learning Models</h3>
                  <p className="text-gray-400">
                    Sophisticated neural networks and ensemble models continuously learn from new data, improving
                    forecast accuracy over time.
                  </p>
                </div>
              </div>

              <div className="flex gap-6 glass-effect p-6 rounded-xl border border-white/5 transition-all duration-300 hover:border-purple-500/50 hover:shadow-md hover:shadow-purple-500/20 group">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center transition-all duration-300 group-hover:bg-purple-500/30 group-hover:scale-110">
                  <Cpu className="h-6 w-6 text-purple-400 group-hover:text-purple-300 transition-colors duration-300" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-purple-400 transition-colors duration-300">Real-time Processing</h3>
                  <p className="text-gray-400">
                    Our system processes incoming weather data in real-time, updating forecasts as conditions change to
                    maintain accuracy.
                  </p>
                </div>
              </div>

              <div className="flex gap-6 glass-effect p-6 rounded-xl border border-white/5 transition-all duration-300 hover:border-amber-500/50 hover:shadow-md hover:shadow-amber-500/20 group">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-amber-500/20 flex items-center justify-center transition-all duration-300 group-hover:bg-amber-500/30 group-hover:scale-110">
                  <BarChart2 className="h-6 w-6 text-amber-400 group-hover:text-amber-300 transition-colors duration-300" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-amber-400 transition-colors duration-300">Adaptive Algorithms</h3>
                  <p className="text-gray-400">
                    Self-correcting algorithms that learn from prediction errors to continuously improve forecast
                    accuracy.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="order-1 lg:order-2 flex justify-center"
          >
            <div className="relative w-full max-w-md">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-green-400 to-blue-500 rounded-2xl blur opacity-30 animate-pulse"></div>
              <div className="relative glass-effect border border-white/10 rounded-2xl p-6 shadow-xl transition-all duration-500 hover:border-white/20 hover:shadow-2xl hover:shadow-blue-500/20 group">
                <Image
                  src="/placeholder.svg?height=400&width=500"
                  alt="AI Prediction Process"
                  width={500}
                  height={400}
                  className="w-full h-auto rounded-xl mb-6 transition-transform duration-500 group-hover:scale-105"
                />
                <div className="space-y-4">
                  <div className="flex items-center gap-2 transition-all duration-300 group-hover:transform group-hover:translate-x-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <p className="text-sm">Data Collection</p>
                    <div className="flex-1 h-0.5 bg-gradient-to-r from-blue-500 to-green-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <p className="text-sm">Processing</p>
                  </div>
                  <div className="flex items-center gap-2 transition-all duration-300 delay-75 group-hover:transform group-hover:translate-x-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <p className="text-sm">Model Training</p>
                    <div className="flex-1 h-0.5 bg-gradient-to-r from-green-500 to-purple-500"></div>
                    <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                    <p className="text-sm">Prediction</p>
                  </div>
                  <div className="flex items-center gap-2 transition-all duration-300 delay-150 group-hover:transform group-hover:translate-x-2">
                    <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                    <p className="text-sm">Validation</p>
                    <div className="flex-1 h-0.5 bg-gradient-to-r from-purple-500 to-amber-500"></div>
                    <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                    <p className="text-sm">Optimization</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}