"use client";

import { TRACKS, type TrackSlug } from "@/lib/types";

interface TrackTabsProps {
  selected: TrackSlug;
  onChange: (slug: TrackSlug) => void;
  available: TrackSlug[];
}

export default function TrackTabs({ selected, onChange, available }: TrackTabsProps) {
  if (available.length <= 1) return null;

  return (
    <div className="flex gap-1 p-1 bg-brand-card border border-white/10 rounded-xl w-fit">
      {TRACKS.filter((t) => available.includes(t.slug)).map((track) => {
        const active = track.slug === selected;
        return (
          <button
            key={track.slug}
            onClick={() => onChange(track.slug)}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${active
                ? "bg-gradient-to-r from-brand-orange to-brand-red text-white shadow-lg shadow-brand-orange/20"
                : "text-brand-muted hover:text-white hover:bg-white/5"
              }
            `}
          >
            <span className="text-base">{track.icon}</span>
            {track.name}
          </button>
        );
      })}
    </div>
  );
}
