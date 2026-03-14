export interface Topic {
  number: number;
  title: string;
  category: "big" | "new" | "worth_knowing";
  categoryLabel: string;
  sourceUrl: string;
  sourceName: string;
  summary: string;
  whyItMatters: string;
}

export interface ParsedDigest {
  title: string;
  dateRange: string;
  topics: Topic[];
}

function matchCategory(name: string): { key: Topic["category"]; label: string } | null {
  const n = name.toLowerCase().replace(/['']/g, "'");
  if (n.includes("big")) return { key: "big", label: "The Big Ones" };
  if (n.includes("new")) return { key: "new", label: "What's New" };
  if (n.includes("worth")) return { key: "worth_knowing", label: "Worth Knowing" };
  return null;
}

export function parseDigest(markdown: string): ParsedDigest {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const topics: Topic[] = [];

  let title = "";
  let dateRange = "";
  let currentCategory: { key: Topic["category"]; label: string } = { key: "new", label: "What's New" };

  const titleMatch = lines[0]?.match(/^#\s+(.+?)(?:\s*-\s*(.+))?$/);
  if (titleMatch) {
    title = titleMatch[1].trim();
    dateRange = titleMatch[2]?.trim() || "";
  }

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    // Section header: ## The Big Ones / ## What's New / ## Worth Knowing
    const sectionMatch = line.match(/^##\s+(.+)$/);
    if (sectionMatch) {
      const sectionName = sectionMatch[1].trim().toLowerCase();
      const matched = matchCategory(sectionName);
      if (matched) {
        currentCategory = matched;
      } else if (sectionName === "raw sources") {
        break; // stop parsing at raw sources
      }
      i++;
      continue;
    }

    // Topic header: ### 1. Title
    const topicMatch = line.match(/^###\s+(\d+)\.\s+(.+)$/);
    if (topicMatch) {
      const number = parseInt(topicMatch[1], 10);
      const topicTitle = topicMatch[2].trim();

      // Collect the body lines until next ### or ##
      const bodyLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].match(/^#{2,3}\s/)) {
        bodyLines.push(lines[i]);
        i++;
      }

      const body = bodyLines.join("\n");
      const { sourceUrl, sourceName, whyItMatters } = extractFields(body);
      const summary = extractSummary(whyItMatters);

      topics.push({
        number,
        title: topicTitle,
        category: currentCategory.key,
        categoryLabel: currentCategory.label,
        sourceUrl,
        sourceName,
        summary,
        whyItMatters,
      });

      continue;
    }

    i++;
  }

  return { title, dateRange, topics };
}

function extractFields(body: string): { sourceUrl: string; sourceName: string; whyItMatters: string } {
  let sourceUrl = "";
  let sourceName = "";
  let whyItMatters = "";

  // Source: [Name](URL)
  const sourceMatch = body.match(/\*\*Source:\*\*\s*\[([^\]]+)\]\(([^)]+)\)/);
  if (sourceMatch) {
    sourceName = sourceMatch[1].trim();
    sourceUrl = sourceMatch[2].trim();
  }

  // Why it matters: text
  const whyMatch = body.match(/\*\*Why it matters:\*\*\s*(.+)/s);
  if (whyMatch) {
    whyItMatters = whyMatch[1]
      .replace(/\n/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  return { sourceUrl, sourceName, whyItMatters };
}

function extractSummary(whyItMatters: string): string {
  if (!whyItMatters) return "";
  const sentences = whyItMatters.match(/[^.!?]+[.!?]+/g);
  if (!sentences) return whyItMatters.slice(0, 120);
  return sentences.slice(0, 2).join("").trim();
}

export function groupByCategory(topics: Topic[]): { category: Topic["category"]; label: string; topics: Topic[] }[] {
  const order: Topic["category"][] = ["big", "new", "worth_knowing"];
  const groups: Map<Topic["category"], Topic[]> = new Map();

  for (const t of topics) {
    if (!groups.has(t.category)) groups.set(t.category, []);
    groups.get(t.category)!.push(t);
  }

  return order
    .filter((cat) => groups.has(cat))
    .map((cat) => ({
      category: cat,
      label: groups.get(cat)![0].categoryLabel,
      topics: groups.get(cat)!,
    }));
}
