"use client"

import { useEffect, useState } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

// Mock data for the chart
const generateMockData = (type: string) => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

  return days.map((day, index) => {
    const baseValue = type === "solar" ? 120 : 80
    const randomFactor = Math.random() * 30 - 15
    const forecastValue = Math.max(0, baseValue + randomFactor)
    const actualValue = Math.max(0, forecastValue + (Math.random() * 20 - 10))

    return {
      day,
      forecast: Math.round(forecastValue),
      actual: Math.round(actualValue),
    }
  })
}

export default function ForecastChart({ type }: { type: string }) {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    setData(generateMockData(type))
  }, [type])

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={data}
        margin={{
          top: 20,
          right: 30,
          left: 20,
          bottom: 10,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
        <XAxis dataKey="day" tick={{ fill: "#9CA3AF" }} />
        <YAxis
          tick={{ fill: "#9CA3AF" }}
          label={{
            value: "Energy (MWh)",
            angle: -90,
            position: "insideLeft",
            style: { fill: "#9CA3AF" },
          }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(17, 24, 39, 0.8)",
            border: "none",
            borderRadius: "8px",
            color: "#F9FAFB",
          }}
        />
        <Legend />
        <Bar name="Forecast" dataKey="forecast" fill={type === "solar" ? "#F59E0B" : "#10B981"} radius={[4, 4, 0, 0]} />
        <Bar name="Actual" dataKey="actual" fill={type === "solar" ? "#FCD34D" : "#34D399"} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

