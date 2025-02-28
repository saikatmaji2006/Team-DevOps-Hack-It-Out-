"use client"

import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

// Mock data for the chart
const generateMockData = (type: string) => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

  return days.map((day, index) => {
    const baseValue = type === "solar" ? 120 : 80
    const randomFactor = Math.random() * 40 - 20
    const forecastValue = Math.max(0, baseValue + randomFactor)

    return {
      day,
      forecast: Math.round(forecastValue),
      confidence: [Math.round(forecastValue * 0.85), Math.round(forecastValue * 1.15)],
    }
  })
}

export default function EnergyChart({ type }: { type: string }) {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    setData(generateMockData(type))
  }, [type])

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart
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
        <Line
          name="Forecast"
          type="monotone"
          dataKey="forecast"
          stroke={type === "solar" ? "#F59E0B" : "#10B981"}
          strokeWidth={3}
          dot={{ r: 6, strokeWidth: 2 }}
          activeDot={{ r: 8 }}
        />
        <Line
          name="Confidence Range"
          type="monotone"
          dataKey="confidence"
          stroke={type === "solar" ? "#FCD34D" : "#34D399"}
          strokeWidth={0}
          dot={false}
          activeDot={false}
          fill={type === "solar" ? "#F59E0B20" : "#10B98120"}
          fillOpacity={0.4}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

