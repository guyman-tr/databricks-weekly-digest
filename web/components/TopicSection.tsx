import type { Topic } from "@/lib/parser";
import TopicCard from "./TopicCard";

interface TopicSectionProps {
  label: string;
  category: Topic["category"];
  topics: Topic[];
}

const SECTION_META: Record<Topic["category"], { icon: string; subtitle: string }> = {
  big:            { icon: "🔥", subtitle: "Developments that could change how you work" },
  new:            { icon: "✦",  subtitle: "New features, releases, and announcements" },
  worth_knowing:  { icon: "📌", subtitle: "Useful context and community highlights" },
};

export default function TopicSection({ label, category, topics }: TopicSectionProps) {
  const meta = SECTION_META[category];

  return (
    <section className="space-y-3">
      <div className="flex items-baseline gap-2">
        <span className="text-lg">{meta.icon}</span>
        <div>
          <h2 className="text-lg font-semibold text-white">{label}</h2>
          <p className="text-xs text-brand-muted">{meta.subtitle}</p>
        </div>
      </div>
      <div className="space-y-2">
        {topics.map((topic) => (
          <TopicCard key={topic.number} topic={topic} />
        ))}
      </div>
    </section>
  );
}
