import HeroSection from "@/components/hero-section"
import FeaturesSection from "@/components/features-section"
import DashboardPreview from "@/components/dashboard-preview"
import AIExplanation from "@/components/ai-explanation"
import GeographicSection from "@/components/geographic-section"
import APISection from "@/components/api-section"
import CTASection from "@/components/cta-section"
import Footer from "@/components/footer"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center">
      <HeroSection />
      <FeaturesSection />
      <DashboardPreview />
      <AIExplanation />
      <GeographicSection />
      <APISection />
      <CTASection />
      <Footer />
    </main>
  )
}

