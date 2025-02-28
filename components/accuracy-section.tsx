"use client"
import Image from "next/image"
import { CheckCircle, AlertCircle, ArrowRight } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"

export default function AccuracySection() {
  return (
    <section className="w-full py-20 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">Accuracy & Optimization</h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our advanced models and error correction techniques narrow the gap between forecasted and actual power
            generation.
          </p>
        </div>

        <Tabs defaultValue="before-after" className="w-full">
          <div className="flex justify-center mb-8">
            <TabsList className="grid grid-cols-2 w-[400px]">
              <TabsTrigger value="before-after">Before & After</TabsTrigger>
              <TabsTrigger value="comparison">Accuracy Comparison</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="before-after">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
              <div className="bg-background border border-border rounded-xl p-6 relative">
                <div className="absolute top-4 right-4 text-red-500">
                  <AlertCircle className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Before Our Solution</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-red-600 dark:text-red-400 text-sm font-bold">✕</span>
                    </div>
                    <p className="text-muted-foreground">Forecasting errors of up to 30% leading to grid instability</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-red-600 dark:text-red-400 text-sm font-bold">✕</span>
                    </div>
                    <p className="text-muted-foreground">Reliance on basic weather forecasts without AI enhancement</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-red-600 dark:text-red-400 text-sm font-bold">✕</span>
                    </div>
                    <p className="text-muted-foreground">
                      Significant financial losses due to inaccurate generation predictions
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-red-600 dark:text-red-400 text-sm font-bold">✕</span>
                    </div>
                    <p className="text-muted-foreground">Manual adjustments required for changing weather conditions</p>
                  </div>
                </div>

                <div className="mt-6">
                  <Image
                    src="/placeholder.svg?height=200&width=400"
                    alt="Before implementation"
                    width={400}
                    height={200}
                    className="w-full h-auto rounded-md"
                  />
                </div>
              </div>

              <div className="bg-background border border-border rounded-xl p-6 relative">
                <div className="absolute top-4 right-4 text-green-500">
                  <CheckCircle className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold mb-4">After Our Solution</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-green-600 dark:text-green-400 text-sm font-bold">✓</span>
                    </div>
                    <p className="text-muted-foreground">
                      Forecasting accuracy improved to 95% for 24-hour predictions
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-green-600 dark:text-green-400 text-sm font-bold">✓</span>
                    </div>
                    <p className="text-muted-foreground">AI-enhanced weather data processing with real-time updates</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-green-600 dark:text-green-400 text-sm font-bold">✓</span>
                    </div>
                    <p className="text-muted-foreground">20% increase in revenue through optimized energy trading</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mt-0.5">
                      <span className="text-green-600 dark:text-green-400 text-sm font-bold">✓</span>
                    </div>
                    <p className="text-muted-foreground">Fully automated adjustments based on changing conditions</p>
                  </div>
                </div>

                <div className="mt-6">
                  <Image
                    src="/placeholder.svg?height=200&width=400"
                    alt="After implementation"
                    width={400}
                    height={200}
                    className="w-full h-auto rounded-md"
                  />
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="comparison">
            <div className="max-w-4xl mx-auto">
              <div className="bg-background border border-border rounded-xl p-6">
                <h3 className="text-xl font-semibold mb-6">Accuracy Comparison with Industry Standards</h3>

                <div className="space-y-8">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="font-medium">24-Hour Forecast Accuracy</span>
                    </div>
                    <div className="relative pt-6">
                      <div className="absolute top-0 left-0 text-sm">Our Solution</div>
                      <div className="w-full bg-muted rounded-full h-4 mb-4">
                        <div className="bg-green-500 h-4 rounded-full" style={{ width: "95%" }}>
                          <span className="absolute right-12 text-xs font-medium text-white px-1">95%</span>
                        </div>
                      </div>

                      <div className="absolute top-0 left-0 text-sm">Industry Average</div>
                      <div className="w-full bg-muted rounded-full h-4 mb-4">
                        <div className="bg-blue-500 h-4 rounded-full" style={{ width: "78%" }}>
                          <span className="absolute right-28 text-xs font-medium text-white px-1">78%</span>
                        </div>
                      </div>

                      <div className="absolute top-0 left-0 text-sm">Traditional Methods</div>
                      <div className="w-full bg-muted rounded-full h-4">
                        <div className="bg-amber-500 h-4 rounded-full" style={{ width: "65%" }}>
                          <span className="absolute right-40 text-xs font-medium text-white px-1">65%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="font-medium">7-Day Forecast Accuracy</span>
                    </div>
                    <div className="relative pt-6">
                      <div className="absolute top-0 left-0 text-sm">Our Solution</div>
                      <div className="w-full bg-muted rounded-full h-4 mb-4">
                        <div className="bg-green-500 h-4 rounded-full" style={{ width: "85%" }}>
                          <span className="absolute right-20 text-xs font-medium text-white px-1">85%</span>
                        </div>
                      </div>

                      <div className="absolute top-0 left-0 text-sm">Industry Average</div>
                      <div className="w-full bg-muted rounded-full h-4 mb-4">
                        <div className="bg-blue-500 h-4 rounded-full" style={{ width: "62%" }}>
                          <span className="absolute right-40 text-xs font-medium text-white px-1">62%</span>
                        </div>
                      </div>

                      <div className="absolute top-0 left-0 text-sm">Traditional Methods</div>
                      <div className="w-full bg-muted rounded-full h-4">
                        <div className="bg-amber-500 h-4 rounded-full" style={{ width: "45%" }}>
                          <span className="absolute right-56 text-xs font-medium text-white px-1">45%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-8 text-center">
                  <Button className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700">
                    View Detailed Analysis <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </section>
  )
}

