import fs from "fs";
import path from "path";

export interface Episode {
  date: string;
  title: string;
  description: string;
  audioFile: string | null;
  itemCount: number;
  digestMarkdown: string;
  hasAudio: boolean;
}

const EPISODES_DIR = path.join(process.cwd(), "public", "episodes");

export function getEpisodeDates(): string[] {
  if (!fs.existsSync(EPISODES_DIR)) return [];

  return fs
    .readdirSync(EPISODES_DIR)
    .filter((name) => {
      const fullPath = path.join(EPISODES_DIR, name);
      return fs.statSync(fullPath).isDirectory() && /^\d{4}-\d{2}-\d{2}$/.test(name);
    })
    .sort()
    .reverse();
}

export function getEpisode(date: string): Episode | null {
  const episodeDir = path.join(EPISODES_DIR, date);
  if (!fs.existsSync(episodeDir)) return null;

  const metaPath = path.join(episodeDir, "meta.json");
  const digestPath = path.join(episodeDir, "digest.md");

  const meta = fs.existsSync(metaPath)
    ? JSON.parse(fs.readFileSync(metaPath, "utf-8"))
    : {};

  const digestMarkdown = fs.existsSync(digestPath)
    ? fs.readFileSync(digestPath, "utf-8")
    : "";

  const audioFile = findAudioFile(episodeDir);

  return {
    date,
    title: meta.title || `Databricks Weekly - ${formatDate(date)}`,
    description: meta.description || "",
    audioFile: audioFile ? `/episodes/${date}/${audioFile}` : null,
    itemCount: meta.itemCount || 0,
    digestMarkdown,
    hasAudio: !!audioFile,
  };
}

export function getAllEpisodes(): Episode[] {
  return getEpisodeDates()
    .map(getEpisode)
    .filter((ep): ep is Episode => ep !== null);
}

export function getLatestEpisode(): Episode | null {
  const dates = getEpisodeDates();
  if (dates.length === 0) return null;
  return getEpisode(dates[0]);
}

function findAudioFile(dir: string): string | null {
  const audioExtensions = [".mp3", ".wav", ".ogg"];
  const files = fs.readdirSync(dir);
  for (const ext of audioExtensions) {
    const match = files.find((f) => f.endsWith(ext));
    if (match) return match;
  }
  return null;
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
