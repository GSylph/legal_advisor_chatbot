import useIntersectionObserver from "../../hooks/useIntersectionObserver.js";
import useCountUp from "../../hooks/useCountUp.js";

const STATS = [
  { label: "Total Queries",   value: 142, suffix: "",  decimals: 0 },
  { label: "Rules Triggered", value: 87,  suffix: "",  decimals: 0 },
  { label: "Audit Entries",   value: 142, suffix: "",  decimals: 0 },
  { label: "Avg. Confidence", value: 82,  suffix: "%", decimals: 0 },
];

function StatCard({ label, value, suffix, decimals }) {
  const [ref, visible] = useIntersectionObserver({ threshold: 0.3 });
  const [, display] = useCountUp(value, { suffix, decimals, enabled: visible });
  return (
    <div ref={ref} className="bg-white rounded-2xl shadow-card border border-zinc-100 p-5 flex flex-col gap-1.5">
      <span className="font-display text-3xl font-black text-zinc-900 tabular-nums">{display}</span>
      <span className="text-xs font-medium text-zinc-400">{label}</span>
    </div>
  );
}

export default function UsageStatsCards() {
  return (
    <div className="bg-white rounded-2xl shadow-card border border-zinc-100 p-7">
      <h2 className="font-semibold text-zinc-800 text-base mb-5">Usage Statistics</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {STATS.map((s) => <StatCard key={s.label} {...s} />)}
      </div>
      <p className="text-[11px] text-zinc-400 mt-4">Illustrative figures — live analytics in a future release.</p>
    </div>
  );
}
