import { useEffect, useRef, useState } from "react";

/**
 * Animates a number from 0 to `target` when `enabled` becomes true.
 * Returns [ref, displayValue] where displayValue is a formatted string.
 */
export default function useCountUp(target, options = {}) {
  const { duration = 1400, decimals = 0, suffix = "", enabled = false } = options;
  const ref = useRef(null);
  const rafRef = useRef(null);

  const format = (n) => n.toFixed(decimals) + suffix;

  const reducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const [displayValue, setDisplayValue] = useState(
    reducedMotion || enabled ? format(target) : format(0)
  );

  useEffect(() => {
    if (!enabled) return;
    if (reducedMotion) {
      setDisplayValue(format(target));
      return;
    }

    const start = performance.now();

    function tick(now) {
      const elapsed = now - start;
      const t = Math.min(elapsed / duration, 1);
      // easeOutQuart
      const eased = 1 - Math.pow(1 - t, 4);
      setDisplayValue(format(target * eased));
      if (t < 1) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        setDisplayValue(format(target));
      }
    }

    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [enabled, target, duration, decimals, suffix, reducedMotion]);

  return [ref, displayValue];
}
