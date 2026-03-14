import { getEpisode, getEpisodeDates, formatDate } from "@/lib/episodes";
import { parseDigest, groupByCategory } from "@/lib/parser";
import AudioPlayer from "@/components/AudioPlayer";
import TopicSection from "@/components/TopicSection";
import Link from "next/link";
import { notFound } from "next/navigation";

export function generateStaticParams() {
  return getEpisodeDates().map((date) => ({ date }));
}

interface PageProps {
  params: { date: string };
}

export default function EpisodePage({ params }: PageProps) {
  const { date } = params;
  const episode = getEpisode(date);

  if (!episode) {
    notFound();
  }

  const parsed = parseDigest(episode.digestMarkdown);
  const groups = groupByCategory(parsed.topics);

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-brand-muted hover:text-brand-orange transition-colors"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
          <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
        </svg>
        Back
      </Link>

      <section className="space-y-1">
        <p className="text-brand-orange text-xs font-semibold tracking-widest uppercase">
          Episode
        </p>
        <h1 className="text-2xl font-bold text-white">
          {parsed.dateRange || formatDate(episode.date)}
        </h1>
        <p className="text-sm text-brand-muted">
          {parsed.topics.length} topics covered
        </p>
      </section>

      {episode.hasAudio && episode.audioFile && (
        <AudioPlayer src={episode.audioFile} title={episode.title} />
      )}

      <div className="space-y-8">
        {groups.map((group) => (
          <TopicSection
            key={group.category}
            label={group.label}
            category={group.category}
            topics={group.topics}
          />
        ))}
      </div>
    </div>
  );
}
