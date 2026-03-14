import fs from "fs";
import path from "path";
import { TRACKS, type TrackSlug, type TrackData, type Episode } from "./types";

export type { TrackSlug, TrackData, Episode };
export { TRACKS, formatDate } from "./types";

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
  const meta = fs.existsSync(metaPath)
    ? JSON.parse(fs.readFileSync(metaPath, "utf-8"))
    : {};

  const tracks: Partial<Record<TrackSlug, TrackData>> = {};

  for (const track of TRACKS) {
    const digestPath = path.join(episodeDir, `digest-${track.slug}.md`);
    if (fs.existsSync(digestPath)) {
      const audioFile = findTrackAudio(episodeDir, track.slug);
      const trackMeta = meta.tracks?.[track.slug] || {};

      tracks[track.slug] = {
        slug: track.slug,
        name: trackMeta.name || track.name,
        digestMarkdown: fs.readFileSync(digestPath, "utf-8"),
        audioFile: audioFile ? `/episodes/${date}/${audioFile}` : null,
        hasAudio: !!audioFile,
        itemCount: trackMeta.itemCount || 0,
        description: trackMeta.description || "",
      };
    }
  }

  // Backward compat: legacy digest.md (no track suffix) maps to "de"
  if (Object.keys(tracks).length === 0) {
    const legacyDigest = path.join(episodeDir, "digest.md");
    if (fs.existsSync(legacyDigest)) {
      const audioFile = findLegacyAudio(episodeDir);
      tracks.de = {
        slug: "de",
        name: "Data Engineering",
        digestMarkdown: fs.readFileSync(legacyDigest, "utf-8"),
        audioFile: audioFile ? `/episodes/${date}/${audioFile}` : null,
        hasAudio: !!audioFile,
        itemCount: meta.itemCount || 0,
        description: meta.description || "",
      };
    }
  }

  if (Object.keys(tracks).length === 0) return null;

  return {
    date,
    title: meta.title || `Databricks Weekly - ${date}`,
    tracks,
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

function findTrackAudio(dir: string, slug: string): string | null {
  const exts = [".mp3", ".wav", ".ogg"];
  const files = fs.readdirSync(dir);
  for (const ext of exts) {
    const target = `podcast-${slug}${ext}`;
    if (files.includes(target)) return target;
  }
  return null;
}

function findLegacyAudio(dir: string): string | null {
  const exts = [".mp3", ".wav", ".ogg"];
  const files = fs.readdirSync(dir);
  for (const ext of exts) {
    const match = files.find((f) => f === `podcast${ext}`);
    if (match) return match;
  }
  return null;
}
