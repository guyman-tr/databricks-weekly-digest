import Link from "next/link";
import { Episode, formatDate } from "@/lib/episodes";

interface EpisodeCardProps {
  episode: Episode;
}

export default function EpisodeCard({ episode }: EpisodeCardProps) {
  return (
    <Link
      href={`/episodes/${episode.date}`}
      className="block bg-brand-card border border-white/5 rounded-xl p-5 hover:border-brand-orange/30 hover:bg-brand-surface transition-all group"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2 min-w-0">
          <p className="text-xs text-brand-orange font-medium">
            {formatDate(episode.date)}
          </p>
          <h3 className="text-white font-semibold group-hover:text-brand-orange transition-colors truncate">
            {episode.title}
          </h3>
          {episode.description && (
            <p className="text-sm text-brand-muted line-clamp-2">
              {episode.description}
            </p>
          )}
          <div className="flex items-center gap-3 text-xs text-brand-muted">
            {episode.hasAudio && (
              <span className="flex items-center gap-1">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
                  <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
                </svg>
                Podcast
              </span>
            )}
            {episode.itemCount > 0 && (
              <span>{episode.itemCount} topics</span>
            )}
          </div>
        </div>
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-brand-orange/10 transition-colors">
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-brand-muted group-hover:text-brand-orange transition-colors">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" />
          </svg>
        </div>
      </div>
    </Link>
  );
}
