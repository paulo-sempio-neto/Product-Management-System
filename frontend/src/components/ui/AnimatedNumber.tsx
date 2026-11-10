import { animate, useReducedMotion } from "motion/react";
import { useEffect, useRef } from "react";

type AnimatedNumberProps = { value: number; format: (value: number) => string };

/** Counts from the previous value to the new one when data changes. */
export default function AnimatedNumber({ value, format }: AnimatedNumberProps) {
  const node = useRef<HTMLSpanElement>(null);
  const previous = useRef(0);
  const reduce = useReducedMotion();

  useEffect(() => {
    const element = node.current;
    if (!element) return;
    if (reduce) {
      element.textContent = format(value);
      previous.current = value;
      return;
    }
    const controls = animate(previous.current, value, {
      duration: 0.9,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (latest) => {
        element.textContent = format(latest);
      },
    });
    previous.current = value;
    return () => controls.stop();
  }, [value, format, reduce]);

  return (
    <span ref={node} className="tabular">
      {format(0)}
    </span>
  );
}
