export type TrackSlug = "de" | "analytics";

export const TRACKS: { slug: TrackSlug; name: string; icon: string }[] = [
  { slug: "de", name: "Data Engineering", icon: "⚙️" },
  { slug: "analytics", name: "Analytics & DS", icon: "📊" },
];

export interface TrackData {
  slug: TrackSlug;
  name: string;
  digestMarkdown: string;
  audioFile: string | null;
  hasAudio: boolean;
  itemCount: number;
  description: string;
}

export interface Episode {
  date: string;
  title: string;
  tracks: Partial<Record<TrackSlug, TrackData>>;
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
