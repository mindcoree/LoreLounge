"use client";

interface LoadingGridProps {
  sidebar?: boolean;
  main?: boolean;
}

export function LoadingGrid({ sidebar = true, main = true }: LoadingGridProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
      {sidebar && (
        <aside className="rounded-2xl border border-white/10 bg-[#171717] p-3 sm:p-4 min-h-[200px]" />
      )}
      {main && <section className="min-h-[200px]" />}
    </div>
  );
}