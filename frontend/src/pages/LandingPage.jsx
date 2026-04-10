import HeroSection          from "../components/landing/HeroSection.jsx";
import FeaturePillars        from "../components/landing/FeaturePillars.jsx";
import PipelineVisualization from "../components/landing/PipelineVisualization.jsx";
import BenchmarkSection      from "../components/landing/BenchmarkSection.jsx";
import ResearchSection       from "../components/landing/ResearchSection.jsx";
import LandingFooter         from "../components/landing/LandingFooter.jsx";

export default function LandingPage() {
  return (
    <div className="font-ui bg-[#EBEBEB] min-h-screen">
      <HeroSection />
      <FeaturePillars />
      <PipelineVisualization />
      <BenchmarkSection />
      <ResearchSection />
      <LandingFooter />
    </div>
  );
}
