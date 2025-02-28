"use client"

import type React from "react"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, ArrowRight } from "lucide-react"

export default function CTASection() {
  const [formState, setFormState] = useState<"idle" | "submitting" | "success">("idle")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormState("submitting")

    // Simulate form submission
    setTimeout(() => {
      setFormState("success")
    }, 1500)
  }

  return (
    <section id="contact" className="w-full py-20 relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-900/10 via-background to-background"></div>

      <div className="container relative z-10 mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full bg-white/5 backdrop-blur-sm">
            <span className="text-sm font-medium gradient-text">Get Started</span>
          </div>
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl mb-4">
            Ready to <span className="gradient-text">Transform</span> Your Energy Forecasting?
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Get in touch to request a demo or learn more about how our AI-driven forecasting system can benefit your
            operations.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <h3 className="text-2xl font-bold mb-6">Benefits for Your Business</h3>

            <div className="space-y-6">
              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300 hover:outline hover:outline-2 hover:outline-offset-4 hover:outline-primary/40">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full animated-gradient-bg flex items-center justify-center">
                    <span className="text-white text-xl font-bold">1</span>
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold mb-2">Increased Revenue</h4>
                    <p className="text-gray-400">
                      Optimize energy trading and reduce imbalance costs with accurate forecasts, increasing revenue by
                      up to 20%.
                    </p>
                  </div>
                </div>
              </div>

              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300 hover:outline hover:outline-2 hover:outline-offset-4 hover:outline-primary/40">
                <div className="flex gap-4">
                  <div
                    className="flex-shrink-0 w-12 h-12 rounded-full animated-gradient-bg flex items-center justify-center"
                    style={{ animationDelay: "0.2s" }}
                  >
                    <span className="text-white text-xl font-bold">2</span>
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold mb-2">Enhanced Grid Stability</h4>
                    <p className="text-gray-400">
                      Improve grid stability and reduce the need for backup power sources with reliable renewable energy
                      forecasts.
                    </p>
                  </div>
                </div>
              </div>

              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300 hover:outline hover:outline-2 hover:outline-offset-4 hover:outline-primary/40">
                <div className="flex gap-4">
                  <div
                    className="flex-shrink-0 w-12 h-12 rounded-full animated-gradient-bg flex items-center justify-center"
                    style={{ animationDelay: "0.4s" }}
                  >
                    <span className="text-white text-xl font-bold">3</span>
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold mb-2">Operational Efficiency</h4>
                    <p className="text-gray-400">
                      Streamline operations and maintenance scheduling based on predicted energy generation patterns.
                    </p>
                  </div>
                </div>
              </div>

              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300 hover:outline hover:outline-2 hover:outline-offset-4 hover:outline-primary/40">
                <div className="flex gap-4">
                  <div
                    className="flex-shrink-0 w-12 h-12 rounded-full animated-gradient-bg flex items-center justify-center"
                    style={{ animationDelay: "0.6s" }}
                  >
                    <span className="text-white text-xl font-bold">4</span>
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold mb-2">Competitive Advantage</h4>
                    <p className="text-gray-400">
                      Stay ahead of competitors with cutting-edge AI technology that continuously improves over time.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <Card className="glass-effect border-white/10 hover:outline hover:outline-2 hover:outline-offset-4 hover:outline-primary/40 transition-all duration-300">
              <CardHeader>
                <CardTitle className="text-2xl">Request a Demo</CardTitle>
                <CardDescription className="text-gray-400">
                  Fill out the form below and our team will get back to you within 24 hours.
                </CardDescription>
              </CardHeader>

              {formState === "success" ? (
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="w-16 h-16 rounded-full animated-gradient-bg flex items-center justify-center mb-4">
                      <CheckCircle className="h-8 w-8 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-2 gradient-text">Thank You!</h3>
                    <p className="text-gray-400 max-w-md">
                      Your request has been submitted successfully. One of our experts will contact you shortly to
                      schedule your personalized demo.
                    </p>
                  </div>
                </CardContent>
              ) : (
                <form onSubmit={handleSubmit}>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label htmlFor="first-name" className="text-sm font-medium">
                          First Name
                        </label>
                        <Input
                          id="first-name"
                          placeholder="John"
                          required
                          className="glass-effect border-white/10 focus:border-white/20 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200"
                        />
                      </div>
                      <div className="space-y-2">
                        <label htmlFor="last-name" className="text-sm font-medium">
                          Last Name
                        </label>
                        <Input
                          id="last-name"
                          placeholder="Doe"
                          required
                          className="glass-effect border-white/10 focus:border-white/20 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="email" className="text-sm font-medium">
                        Email
                      </label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="john.doe@company.com"
                        required
                        className="glass-effect border-white/10 focus:border-white/20 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200"
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="company" className="text-sm font-medium">
                        Company
                      </label>
                      <Input
                        id="company"
                        placeholder="Acme Inc."
                        required
                        className="glass-effect border-white/10 focus:border-white/20 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200"
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="message" className="text-sm font-medium">
                        Message
                      </label>
                      <Textarea
                        id="message"
                        placeholder="Tell us about your specific needs and interests..."
                        rows={4}
                        className="glass-effect border-white/10 focus:border-white/20 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200"
                      />
                    </div>
                  </CardContent>

                  <CardFooter>
                    <Button
                      type="submit"
                      className="w-full animated-gradient-bg hover:opacity-90 text-white font-medium hover:outline hover:outline-2 hover:outline-offset-2 hover:outline-white/30 transition-all duration-200"
                      disabled={formState === "submitting"}
                    >
                      {formState === "submitting" ? (
                        <span className="flex items-center">
                          <svg
                            className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            ></circle>
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                          </svg>
                          Submitting...
                        </span>
                      ) : (
                        <span className="flex items-center">
                          Request Demo <ArrowRight className="ml-2 h-5 w-5" />
                        </span>
                      )}
                    </Button>
                  </CardFooter>
                </form>
              )}
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  )
}