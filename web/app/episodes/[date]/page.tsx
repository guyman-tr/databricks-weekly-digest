import { getEpisode, getEpisodeDates } from "@/lib/episodes";
import EpisodeList from "@/components/EpisodeList";
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

  return (
    <div>
      <div className="max-w-3xl mx-auto px-6 pt-6">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm text-brand-muted hover:text-brand-orange transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
          </svg>
          Back
        </Link>
      </div>
      <EpisodeList episodes={[episode]} />
    </div>
  );
}
