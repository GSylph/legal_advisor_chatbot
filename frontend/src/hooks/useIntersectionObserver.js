import { useEffect, useRef, useState } from "react";

/**
 * Returns [ref, isVisible].
 * Attaches an IntersectionObserver to the ref'd element.
 * isVisible flips to true once the element enters the viewport and stays true.
 * Respects prefers-reduced-motion: starts visible immediately if motion is reduced.
 */
export default function useIntersectionObserver(options = {}) {
  const ref = useRef(null);
  const reducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const [isVisible, setIsVisible] = useState(reducedMotion);

  useEffect(() => {
    if (reducedMotion) return;
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      {
        threshold: options.threshold ?? 0.15,
        rootMargin: options.rootMargin ?? "0px 0px -40px 0px",
      }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [reducedMotion, options.threshold, options.rootMargin]);

  return [ref, isVisible];
}
