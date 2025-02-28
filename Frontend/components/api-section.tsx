"use client"

import { motion } from "framer-motion"
import { Code, FileJson, Server, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function APISection() {
  return (
    <section id="api" className="w-full py-20 relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-blue-900/10 via-background to-background"></div>

      <div className="container relative z-10 mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full bg-white/5 backdrop-blur-sm hover:outline hover:outline-2 hover:outline-white/20 transition-all duration-300">
            <span className="text-sm font-medium gradient-text">Developer Tools</span>
          </div>
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl mb-4">
            <span className="gradient-text">Robust API</span> Integration
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Seamlessly integrate our forecasting capabilities with your existing energy management systems.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <div className="space-y-6">
              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 hover:outline hover:outline-2 hover:outline-blue-500/30 transition-all duration-300">
                <div className="flex gap-4 mb-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center hover:outline hover:outline-2 hover:outline-blue-400/50 transition-all duration-300">
                    <Server className="h-6 w-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">RESTful API</h3>
                    <p className="text-gray-400">
                      Our comprehensive REST API provides easy access to forecasts, historical data, and real-time
                      updates with robust authentication.
                    </p>
                  </div>
                </div>
                <div className="ml-16 pl-2 border-l-2 border-blue-500/30">
                  <p className="text-sm text-blue-400">GET /api/v1/forecast/{"{location_id}"}</p>
                </div>
              </div>

              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 hover:outline hover:outline-2 hover:outline-green-500/30 transition-all duration-300">
                <div className="flex gap-4 mb-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center hover:outline hover:outline-2 hover:outline-green-400/50 transition-all duration-300">
                    <FileJson className="h-6 w-6 text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Structured Data</h3>
                    <p className="text-gray-400">
                      All data is returned in well-structured JSON format with comprehensive documentation and schema
                      validation.
                    </p>
                  </div>
                </div>
                <div className="ml-16 pl-2 border-l-2 border-green-500/30">
                  <p className="text-sm text-green-400">{'{ "forecast": { "daily_total_mwh": 1250.8 } }'}</p>
                </div>
              </div>

              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 hover:outline hover:outline-2 hover:outline-purple-500/30 transition-all duration-300">
                <div className="flex gap-4 mb-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center hover:outline hover:outline-2 hover:outline-purple-400/50 transition-all duration-300">
                    <Zap className="h-6 w-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Real-time Webhooks</h3>
                    <p className="text-gray-400">
                      Subscribe to real-time updates via webhooks to receive instant notifications when forecasts change
                      significantly.
                    </p>
                  </div>
                </div>
                <div className="ml-16 pl-2 border-l-2 border-purple-500/30">
                  <p className="text-sm text-purple-400">POST /api/v1/webhooks/subscribe</p>
                </div>
              </div>

              <div className="glass-effect p-6 rounded-xl border border-white/10 hover:border-white/20 hover:outline hover:outline-2 hover:outline-amber-500/30 transition-all duration-300">
                <div className="flex gap-4 mb-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-amber-500/20 flex items-center justify-center hover:outline hover:outline-2 hover:outline-amber-400/50 transition-all duration-300">
                    <Code className="h-6 w-6 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Client Libraries</h3>
                    <p className="text-gray-400">
                      Official client libraries available for JavaScript, Python, Java, and C# to simplify integration
                      with your systems.
                    </p>
                  </div>
                </div>
                <div className="ml-16 pl-2 border-l-2 border-amber-500/30">
                  <p className="text-sm text-amber-400">npm install @energyai/client</p>
                </div>
              </div>
            </div>

            <div className="mt-8">
              <Button className="animated-gradient-bg hover:opacity-90 hover:outline hover:outline-2 hover:outline-white/30 text-white font-medium transition-all duration-300">
                Explore API Documentation
              </Button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <Tabs defaultValue="get" className="w-full">
              <TabsList className="grid grid-cols-3 w-full mb-6 glass-effect hover:outline hover:outline-2 hover:outline-white/20 transition-all duration-300">
                <TabsTrigger value="get" className="data-[state=active]:gradient-text hover:outline hover:outline-1 hover:outline-blue-400/30 transition-all duration-300">
                  GET
                </TabsTrigger>
                <TabsTrigger value="post" className="data-[state=active]:gradient-text hover:outline hover:outline-1 hover:outline-purple-400/30 transition-all duration-300">
                  POST
                </TabsTrigger>
                <TabsTrigger value="webhook" className="data-[state=active]:gradient-text hover:outline hover:outline-1 hover:outline-green-400/30 transition-all duration-300">
                  Webhook
                </TabsTrigger>
              </TabsList>

              <div className="glass-effect rounded-xl p-4 font-mono text-sm border border-white/10 hover:border-white/20 hover:outline hover:outline-2 hover:outline-white/20 transition-all duration-300">
                <TabsContent value="get" className="mt-0">
                  <div className="text-green-400 mb-2">// Get forecast for a specific location</div>
                  <div className="mb-4 text-blue-400">GET /api/v1/forecast/{"{location_id}"}</div>

                  <div className="text-green-400 mb-2">// Response</div>
                  <pre className="bg-background/50 p-4 rounded border border-white/5 hover:border-white/10 hover:outline hover:outline-1 hover:outline-blue-500/20 transition-all duration-300 overflow-x-auto">
                    {`{
  "location": {
    "id": "solar-farm-1",
    "name": "Solar Farm Alpha",
    "coordinates": {
      "lat": 34.0522,
      "lng": -118.2437
    }
  },
  "forecast": {
    "date": "2025-02-28",
    "hourly": [
      {
        "hour": 8,
        "solar_output_kw": 120.5,
        "confidence": 0.95,
        "weather": {
          "cloud_cover": 0.2,
          "temperature": 22
        }
      },
      // Additional hours...
    ],
    "daily_total_mwh": 1250.8,
    "peak_hour": 13
  }
}`}
                  </pre>
                </TabsContent>

                <TabsContent value="post" className="mt-0">
                  <div className="text-green-400 mb-2">// Request custom forecast</div>
                  <div className="mb-4 text-purple-400">POST /api/v1/forecast/custom</div>

                  <div className="text-green-400 mb-2">// Request Body</div>
                  <pre className="bg-background/50 p-4 rounded border border-white/5 hover:border-white/10 hover:outline hover:outline-1 hover:outline-purple-500/20 transition-all duration-300 overflow-x-auto mb-4">
                    {`{
  "location_id": "wind-farm-2",
  "start_date": "2025-03-01",
  "end_date": "2025-03-07",
  "resolution": "hourly",
  "parameters": {
    "include_weather": true,
    "confidence_intervals": true
  }
}`}
                  </pre>

                  <div className="text-green-400 mb-2">// Response</div>
                  <pre className="bg-background/50 p-4 rounded border border-white/5 hover:border-white/10 hover:outline hover:outline-1 hover:outline-purple-500/20 transition-all duration-300 overflow-x-auto">
                    {`{
  "request_id": "f8c3de3d-1fea-4d7c-a8b0-29f63c4c3454",
  "status": "processing",
  "eta_seconds": 15,
  "callback_url": "/api/v1/forecast/custom/f8c3de3d-1fea-4d7c-a8b0-29f63c4c3454"
}`}
                  </pre>
                </TabsContent>

                <TabsContent value="webhook" className="mt-0">
                  <div className="text-green-400 mb-2">// Webhook payload for forecast updates</div>
                  <pre className="bg-background/50 p-4 rounded border border-white/5 hover:border-white/10 hover:outline hover:outline-1 hover:outline-green-500/20 transition-all duration-300 overflow-x-auto">
                    {`{
  "event_type": "forecast_updated",
  "timestamp": "2025-02-28T15:30:45Z",
  "location_id": "solar-farm-1",
  "changes": {
    "previous_daily_total_mwh": 1250.8,
    "new_daily_total_mwh": 1180.5,
    "change_percentage": -5.6,
    "reason": "Unexpected cloud formation detected",
    "confidence": 0.92
  },
  "forecast_url": "/api/v1/forecast/solar-farm-1"
}`}
                  </pre>
                </TabsContent>
              </div>
            </Tabs>
          </motion.div>
        </div>
      </div>
    </section>
  )
}