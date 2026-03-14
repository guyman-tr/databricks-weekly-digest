"use client";

import { useState, useMemo } from "react";
import type { Episode, TrackSlug, TrackData } from "@/lib/types";
import { TRACKS, formatDate } from "@/lib/types";
import { parseDigest, groupByCategory } from "@/lib/parser";
import AudioPlayer from "@/components/AudioPlayer";
import TopicSection from "@/components/TopicSection";
import TrackTabs from "@/components/TrackTabs";

interface EpisodeListProps {
  episodes: Episode[];
}

export default function EpisodeList({ episodes }: EpisodeListProps) {
  const availableTracks = useMemo(() => {
    const slugs = new Set<TrackSlug>();
    for (const ep of episodes) {
      for (const slug of Object.keys(ep.tracks) as TrackSlug[]) {
        slugs.add(slug);
      }
    }
    return TRACKS.map((t) => t.slug).filter((s) => slugs.has(s));
  }, [episodes]);

  const [selectedTrack, setSelectedTrack] = useState<TrackSlug>(
    availableTracks[0] || "de"
  );

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-10">
      <div className="flex justify-center">
        <TrackTabs
          selected={selectedTrack}
          onChange={setSelectedTrack}
          available={availableTracks}
        />
      </div>

      <div className="space-y-16">
        {episodes.map((episode) => {
          const trackData: TrackData | undefined = episode.tracks[selectedTrack];

          if (!trackData) {
            const fallback = Object.values(episode.tracks)[0];
            if (!fallback) return null;
            return (
              <EpisodeArticle
                key={episode.date}
                date={episode.date}
                trackData={fallback}
                trackLabel={fallback.name}
              />
            );
          }

          return (
            <EpisodeArticle
              key={episode.date}
              date={episode.date}
              trackData={trackData}
            />
          );
        })}
      </div>
    </div>
  );
}

function EpisodeArticle({
  date,
  trackData,
  trackLabel,
}: {
  date: string;
  trackData: TrackData;
  trackLabel?: string;
}) {
  const parsed = parseDigest(trackData.digestMarkdown);
  const groups = groupByCategory(parsed.topics);

  return (
    <article className="space-y-6">
      <section className="space-y-1">
        <p className="text-brand-orange text-xs font-semibold tracking-widest uppercase">
          Episode{trackLabel ? ` · ${trackLabel}` : ""}
        </p>
        <h2 className="text-2xl font-bold text-white">
          {parsed.dateRange || formatDate(date)}
        </h2>
        <p className="text-sm text-brand-muted">
          {parsed.topics.length} topics covered
        </p>
      </section>

      {trackData.hasAudio && trackData.audioFile && (
        <AudioPlayer
          src={trackData.audioFile}
          title={`${trackData.name} – ${formatDate(date)}`}
        />
      )}

      <div className="space-y-8">
        {groups.map((group) => (
          <TopicSection
            key={`${date}-${group.category}`}
            label={group.label}
            category={group.category}
            topics={group.topics}
          />
        ))}
      </div>
    </article>
  );
}
