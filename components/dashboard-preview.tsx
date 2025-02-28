"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Sun, Wind, Cloud, ArrowUpRight, ArrowDownRight } from "lucide-react"
import EnergyChart from "./charts/energy-chart"
import ForecastChart from "./charts/forecast-chart"

export default function DashboardPreview() {
  const [activeTab, setActiveTab] = useState("solar")

  return (
    <section id="dashboard" className="w-full py-20 relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-blue-900/10 via-background to-background"></div>

      <div className="container relative z-10 mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full bg-white/5 backdrop-blur-sm">
            <span className="text-sm font-medium gradient-text">Interactive Dashboard</span>
          </div>
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl mb-4">
            Visualize <span className="gradient-text">Energy Forecasts</span> in Real-Time
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Our intuitive dashboard provides actionable insights at a glance, helping you make informed decisions.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="max-w-6xl mx-auto"
        >
          <Tabs defaultValue="solar" className="w-full" onValueChange={setActiveTab}>
            <div className="flex justify-center mb-8">
              <TabsList className="grid grid-cols-2 w-[400px] glass-effect transition-all duration-300 hover:shadow-md hover:shadow-blue-500/20">
                <TabsTrigger value="solar" className="flex items-center gap-2 data-[state=active]:gradient-text group transition-all duration-300">
                  <Sun className="h-4 w-4 group-hover:text-blue-400 transition-colors" /> Solar Energy
                </TabsTrigger>
                <TabsTrigger value="wind" className="flex items-center gap-2 data-[state=active]:gradient-text group transition-all duration-300">
                  <Wind className="h-4 w-4 group-hover:text-green-400 transition-colors" /> Wind Energy
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2 glass-effect border-white/5 transition-all duration-300 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10 group">
                <CardHeader>
                  <CardTitle className="group-hover:gradient-text transition-colors duration-300">Energy Generation Forecast</CardTitle>
                  <CardDescription>
                    {activeTab === "solar"
                      ? "Predicted solar energy output for the next 7 days"
                      : "Predicted wind energy output for the next 7 days"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[350px]">
                    <EnergyChart type={activeTab} />
                  </div>
                </CardContent>
              </Card>

              <div className="flex flex-col gap-6">
                <Card className="glass-effect border-white/5 transition-all duration-300 hover:border-green-500/50 hover:shadow-lg hover:shadow-green-500/10 group">
                  <CardHeader>
                    <CardTitle className="group-hover:gradient-text transition-colors duration-300">Accuracy Metrics</CardTitle>
                    <CardDescription>Forecast precision analysis</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-1">
                          <span>24-Hour Forecast</span>
                          <span className="font-medium text-green-400 flex items-center">
                            96% <ArrowUpRight className="ml-1 h-3 w-3" />
                          </span>
                        </div>
                        <div className="w-full bg-white/5 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full"
                            style={{ width: "96%" }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between mb-1">
                          <span>48-Hour Forecast</span>
                          <span className="font-medium text-green-400 flex items-center">
                            92% <ArrowUpRight className="ml-1 h-3 w-3" />
                          </span>
                        </div>
                        <div className="w-full bg-white/5 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full"
                            style={{ width: "92%" }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between mb-1">
                          <span>7-Day Forecast</span>
                          <span className="font-medium text-yellow-400 flex items-center">
                            85% <ArrowDownRight className="ml-1 h-3 w-3" />
                          </span>
                        </div>
                        <div className="w-full bg-white/5 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-yellow-400 to-amber-500 h-2 rounded-full"
                            style={{ width: "85%" }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="glass-effect border-white/5 transition-all duration-300 hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10 group">
                  <CardHeader>
                    <CardTitle className="group-hover:gradient-text transition-colors duration-300">Weather Conditions</CardTitle>
                    <CardDescription>Current factors affecting generation</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center mr-3 group-hover:bg-blue-500/30 transition-colors duration-300">
                          <Cloud className="h-6 w-6 text-blue-400" />
                        </div>
                        <div>
                          <p className="font-medium">Cloud Cover</p>
                          <p className="text-sm text-gray-400">23% coverage</p>
                        </div>
                      </div>
                      <span className="text-green-400 font-medium">Favorable</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center mr-3 group-hover:bg-green-500/30 transition-colors duration-300">
                          <Wind className="h-6 w-6 text-green-400" />
                        </div>
                        <div>
                          <p className="font-medium">Wind Speed</p>
                          <p className="text-sm text-gray-400">18 km/h</p>
                        </div>
                      </div>
                      <span className="text-green-400 font-medium">Optimal</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            <div className="mt-6">
              <Card className="glass-effect border-white/5 transition-all duration-300 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10 group">
                <CardHeader>
                  <CardTitle className="group-hover:gradient-text transition-colors duration-300">Forecast Accuracy Comparison</CardTitle>
                  <CardDescription>Predicted vs. actual energy generation</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ForecastChart type={activeTab} />
                  </div>
                </CardContent>
              </Card>
            </div>
          </Tabs>
        </motion.div>
      </div>
    </section>
  )
}