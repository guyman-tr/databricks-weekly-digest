import { getAllEpisodes } from "@/lib/episodes";
import EpisodeList from "@/components/EpisodeList";

export default function Home() {
  const allEpisodes = getAllEpisodes();

  if (allEpisodes.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20 text-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-orange to-brand-red flex items-center justify-center mx-auto mb-6">
          <svg viewBox="0 0 24 24" fill="white" className="w-8 h-8">
            <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
          </svg>
        </div>
        <h2 className="text-2xl font-semibold text-white mb-3">No episodes yet</h2>
        <p className="text-brand-muted max-w-md mx-auto">
          Run the digest pipeline to generate your first episode.
        </p>
        <pre className="mt-6 text-sm bg-brand-card border border-white/10 rounded-lg p-4 inline-block text-left text-brand-muted font-mono">
          python run.py
        </pre>
      </div>
    );
  }

  return <EpisodeList episodes={allEpisodes} />;
}
