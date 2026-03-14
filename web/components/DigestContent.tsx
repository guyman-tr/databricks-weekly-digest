"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface DigestContentProps {
  markdown: string;
}

export default function DigestContent({ markdown }: DigestContentProps) {
  return (
    <article className="prose prose-invert max-w-none
      prose-headings:font-semibold
      prose-h1:text-2xl prose-h1:text-white prose-h1:border-b prose-h1:border-white/10 prose-h1:pb-4
      prose-h2:text-xl prose-h2:text-brand-orange prose-h2:mt-10
      prose-h3:text-lg prose-h3:text-white/90
      prose-p:text-brand-muted prose-p:leading-relaxed
      prose-a:text-brand-orange prose-a:no-underline hover:prose-a:underline
      prose-strong:text-white
      prose-li:text-brand-muted
      prose-ul:space-y-1
      prose-hr:border-white/10
    ">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
    </article>
  );
}
