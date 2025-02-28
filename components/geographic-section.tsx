"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import Image from "next/image"
import { MapPin, Sun, Wind, Cloud } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const locations = [
  {
    id: "north",
    name: "Northern Region",
    coordinates: { x: 30, y: 20 },
    solar: { efficiency: 85, forecast: "120 MWh" },
    wind: { efficiency: 92, forecast: "180 MWh" },
    weather: "Partly Cloudy, 18°C",
  },
  {
    id: "south",
    name: "Southern Region",
    coordinates: { x: 30, y: 70 },
    solar: { efficiency: 95, forecast: "210 MWh" },
    wind: { efficiency: 78, forecast: "90 MWh" },
    weather: "Sunny, 32°C",
  },
  {
    id: "east",
    name: "Eastern Region",
    coordinates: { x: 70, y: 45 },
    solar: { efficiency: 88, forecast: "150 MWh" },
    wind: { efficiency: 90, forecast: "160 MWh" },
    weather: "Cloudy, 22°C",
  },
  {
    id: "west",
    name: "Western Region",
    coordinates: { x: 15, y: 45 },
    solar: { efficiency: 80, forecast: "110 MWh" },
    wind: { efficiency: 96, forecast: "220 MWh" },
    weather: "Windy, 16°C",
  },
]

export default function GeographicSection() {
  const [selectedLocation, setSelectedLocation] = useState(locations[0])
  const [activeTab, setActiveTab] = useState("solar")

  return (
    <section className="w-full py-20 relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-green-900/10 via-background to-background"></div>

      <div className="container relative z-10 mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full bg-white/5 backdrop-blur-sm">
            <span className="text-sm font-medium gradient-text">Location Intelligence</span>
          </div>
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl mb-4">
            <span className="gradient-text">Geographic</span> Adaptability
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Our system provides tailored forecasts based on specific locations and their unique weather patterns.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="relative"
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-green-400 to-blue-500 rounded-2xl blur opacity-20"></div>
            <div className="aspect-square relative rounded-xl overflow-hidden border border-white/10 glass-effect">
              <Image
                src="/placeholder.svg?height=600&width=600"
                alt="Geographic map"
                width={600}
                height={600}
                className="w-full h-full object-cover opacity-80"
              />

              {locations.map((location) => (
                <button
                  key={location.id}
                  className={`absolute transform -translate-x-1/2 -translate-y-1/2 group z-20`}
                  style={{
                    left: `${location.coordinates.x}%`,
                    top: `${location.coordinates.y}%`,
                  }}
                  onClick={() => setSelectedLocation(location)}
                >
                  <div
                    className={`
                    flex items-center justify-center w-8 h-8 rounded-full 
                    ${
                      selectedLocation.id === location.id
                        ? "animated-gradient-bg glow relative z-10"
                        : "bg-white/10 backdrop-blur-sm hover:bg-white/20"
                    }
                    transition-all duration-300
                    group-hover:outline group-hover:outline-2 group-hover:outline-offset-4 group-hover:outline-primary/50
                  `}
                  >
                    <MapPin className="h-4 w-4" />
                  </div>
                  <div
                    className={`
                    absolute top-full left-1/2 transform -translate-x-1/2 mt-2
                    glass-effect border border-white/10 rounded-md px-3 py-1.5
                    text-sm font-medium shadow-sm
                    opacity-0 group-hover:opacity-100 transition-opacity duration-200
                    ${selectedLocation.id === location.id ? "opacity-100" : ""}
                  `}
                  >
                    {location.name}
                  </div>

                  {selectedLocation.id === location.id && (
                    <div className="absolute w-16 h-16 rounded-full border-2 border-primary/50 animate-ping -top-4 -left-4"></div>
                  )}
                </button>
              ))}

              <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent"></div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <Card className="glass-effect border-white/10 hover:outline hover:outline-2 hover:outline-offset-4 hover:outline-primary/40 transition-all duration-300">
              <CardContent className="p-6">
                <div className="mb-6">
                  <h3 className="text-2xl font-bold mb-2 gradient-text">{selectedLocation.name}</h3>
                  <div className="flex items-center text-gray-400">
                    <Cloud className="h-5 w-5 mr-2" />
                    <span>{selectedLocation.weather}</span>
                  </div>
                </div>

                <Tabs defaultValue="solar" className="w-full" onValueChange={setActiveTab}>
                  <TabsList className="grid grid-cols-2 w-full mb-6 glass-effect">
                    <TabsTrigger value="solar" className="flex items-center gap-2 data-[state=active]:gradient-text">
                      <Sun className="h-4 w-4" /> Solar Energy
                    </TabsTrigger>
                    <TabsTrigger value="wind" className="flex items-center gap-2 data-[state=active]:gradient-text">
                      <Wind className="h-4 w-4" /> Wind Energy
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="solar" className="space-y-6">
                    <div>
                      <h4 className="text-lg font-medium mb-2">Solar Efficiency</h4>
                      <div className="w-full bg-white/5 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-amber-400 to-yellow-500 h-3 rounded-full"
                          style={{ width: `${selectedLocation.solar.efficiency}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between mt-1 text-sm">
                        <span>Efficiency</span>
                        <span className="font-medium text-amber-400">{selectedLocation.solar.efficiency}%</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-lg font-medium mb-2">Forecast Details</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="glass-effect rounded-lg p-4 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200">
                          <p className="text-sm text-gray-400">Daily Output</p>
                          <p className="text-2xl font-bold gradient-text">{selectedLocation.solar.forecast}</p>
                        </div>
                        <div className="glass-effect rounded-lg p-4 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200">
                          <p className="text-sm text-gray-400">Peak Hours</p>
                          <p className="text-2xl font-bold gradient-text">10:00 - 14:00</p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="wind" className="space-y-6">
                    <div>
                      <h4 className="text-lg font-medium mb-2">Wind Efficiency</h4>
                      <div className="w-full bg-white/5 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-green-400 to-emerald-500 h-3 rounded-full"
                          style={{ width: `${selectedLocation.wind.efficiency}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between mt-1 text-sm">
                        <span>Efficiency</span>
                        <span className="font-medium text-green-400">{selectedLocation.wind.efficiency}%</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-lg font-medium mb-2">Forecast Details</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="glass-effect rounded-lg p-4 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200">
                          <p className="text-sm text-gray-400">Daily Output</p>
                          <p className="text-2xl font-bold gradient-text">{selectedLocation.wind.forecast}</p>
                        </div>
                        <div className="glass-effect rounded-lg p-4 hover:outline hover:outline-2 hover:outline-primary/30 hover:outline-offset-2 transition-all duration-200">
                          <p className="text-sm text-gray-400">Wind Speed</p>
                          <p className="text-2xl font-bold gradient-text">18 km/h</p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  )
}