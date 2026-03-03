import HeroSection from '../components/main/HeroSection'
import HowWeWorkSection from '../components/main/HowWeWorkSection'
import AboutUsSection from '../components/main/AboutUsSection'
import StatsSection from '../components/main/StatsSection'
import AllBotsSection from '../components/main/AllBotsSection'
import TestimonialsSection from '../components/main/TestimonialsSection'


export default function Home() {
  return (
    <main>
      <HeroSection />
      <HowWeWorkSection />
      <AboutUsSection />
      <StatsSection />
      <AllBotsSection />
      <TestimonialsSection />
    </main>
  )
}