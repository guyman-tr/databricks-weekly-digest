"use client";

import { useState } from "react";
import type { Topic } from "@/lib/parser";

type ExpandState = "collapsed" | "summary" | "full";

const CATEGORY_STYLES: Record<Topic["category"], { dot: string; badge: string }> = {
  big:            { dot: "bg-brand-orange",  badge: "text-brand-orange bg-brand-orange/10 border-brand-orange/20" },
  new:            { dot: "bg-blue-400",      badge: "text-blue-400 bg-blue-400/10 border-blue-400/20" },
  worth_knowing:  { dot: "bg-emerald-400",   badge: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20" },
};

function ExternalLinkIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-3.5 h-3.5 flex-shrink-0">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" strokeLinecap="round" strokeLinejoin="round"/>
      <polyline points="15 3 21 3 21 9" strokeLinecap="round" strokeLinejoin="round"/>
      <line x1="10" y1="14" x2="21" y2="3" strokeLinecap="round"/>
    </svg>
  );
}

export default function TopicCard({ topic }: { topic: Topic }) {
  const [state, setState] = useState<ExpandState>("collapsed");
  const styles = CATEGORY_STYLES[topic.category];

  function cycle() {
    const next: Record<ExpandState, ExpandState> = {
      collapsed: "summary",
      summary: "full",
      full: "collapsed",
    };
    setState(next[state]);
  }

  const isYouTube = topic.sourceUrl.includes("youtube.com") || topic.sourceUrl.includes("youtu.be");
  const sourceType = isYouTube ? "YouTube" : "Blog";
  const expanded = state !== "collapsed";

  return (
    <div
      className={`
        border rounded-xl transition-all duration-200 overflow-hidden cursor-pointer
        ${expanded
          ? "bg-brand-surface border-white/10"
          : "bg-brand-card border-white/5 hover:border-white/15"
        }
      `}
      onClick={cycle}
    >
      {/* Header - always visible */}
      <div className="px-5 py-4 flex items-start gap-4">
        <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${styles.dot}`} />
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-medium leading-snug pr-8">
            {topic.title}
          </h3>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${styles.badge}`}>
            {sourceType}
          </span>
          <svg
            viewBox="0 0 24 24"
            fill="currentColor"
            className={`w-4 h-4 text-brand-muted transition-transform duration-200 ${
              expanded ? "rotate-180" : ""
            }`}
          >
            <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6z" />
          </svg>
        </div>
      </div>

      {/* Level 1: Summary + source link */}
      {expanded && (
        <div className="px-5 pb-4 pl-11">
          <p className="text-sm text-gray-300 leading-relaxed">
            {topic.summary}
          </p>
          <a
            href={topic.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1.5 text-xs text-brand-orange hover:underline mt-2"
          >
            <ExternalLinkIcon />
            {sourceTruncated(topic.sourceName)}
          </a>
        </div>
      )}

      {/* Level 2: Full "Why it matters" analysis */}
      {state === "full" && (
        <div className="px-5 pb-5 pl-11">
          <div className="border-t border-white/5 pt-3">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-brand-muted mb-2">
              Why it matters
            </p>
            <p className="text-sm text-gray-300 leading-relaxed">
              {topic.whyItMatters}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function sourceTruncated(name: string): string {
  return name.length > 60 ? name.slice(0, 57) + "..." : name;
}
