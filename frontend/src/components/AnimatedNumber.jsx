import { useEffect, useRef, useState } from "react";

/**
 * AnimatedNumber
 *
 * Counts up from 0 to `value` over a short duration whenever `value`
 * changes, instead of just popping the digit in. Small touch, but it's
 * exactly the kind of thing that makes a dashboard feel alive rather than
 * a static printout of numbers.
 */
export default function AnimatedNumber({ value, duration = 600 }) {
  const [display, setDisplay] = useState(0);
  const startRef = useRef(null);
  const fromRef = useRef(0);

  useEffect(() => {
    fromRef.current = display;
    startRef.current = null;
    let frameId;

    function step(timestamp) {
      if (startRef.current === null) startRef.current = timestamp;
      const progress = Math.min((timestamp - startRef.current) / duration, 1);
      // ease-out cubic — starts fast, settles gently, feels less mechanical
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(fromRef.current + (value - fromRef.current) * eased);
      setDisplay(current);
      if (progress < 1) {
        frameId = requestAnimationFrame(step);
      }
    }

    frameId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frameId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return <>{display}</>;
}
