/**
 * Skeleton
 *
 * A shimmering placeholder shown while content loads, instead of a blank
 * space + spinner. Used for document/collection lists so the layout
 * doesn't jump once real data arrives — the skeleton roughly matches the
 * shape of what's coming.
 */
export default function Skeleton({ variant = "line", count = 1 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`skeleton skeleton-${variant}`} />
      ))}
    </>
  );
}
