"use client";

import { useRef, useState, useEffect, useCallback } from "react";

interface AudioPlayerProps {
  src: string;
  title: string;
}

const SPEEDS = [0.75, 1, 1.25, 1.5, 2];

export default function AudioPlayer({ src, title }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speedIdx, setSpeedIdx] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTime = () => setCurrentTime(audio.currentTime);
    const onMeta = () => setDuration(audio.duration);
    const onEnd = () => setIsPlaying(false);

    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onMeta);
    audio.addEventListener("ended", onEnd);

    return () => {
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("loadedmetadata", onMeta);
      audio.removeEventListener("ended", onEnd);
    };
  }, []);

  const togglePlay = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const seek = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const audio = audioRef.current;
      const bar = progressRef.current;
      if (!audio || !bar || !duration) return;
      const rect = bar.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      audio.currentTime = ratio * duration;
    },
    [duration]
  );

  const cycleSpeed = useCallback(() => {
    const next = (speedIdx + 1) % SPEEDS.length;
    setSpeedIdx(next);
    if (audioRef.current) {
      audioRef.current.playbackRate = SPEEDS[next];
    }
  }, [speedIdx]);

  const skip = useCallback((seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(audio.duration, audio.currentTime + seconds));
  }, []);

  const progress = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-brand-surface border border-white/10 rounded-2xl p-5 space-y-4">
      <audio ref={audioRef} src={src} preload="metadata" />

      <div className="flex items-center gap-2 text-brand-muted text-xs">
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-brand-orange">
          <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
        </svg>
        <span className="font-medium text-white truncate">{title}</span>
      </div>

      {/* Progress bar */}
      <div
        ref={progressRef}
        onClick={seek}
        className="h-2 bg-white/10 rounded-full cursor-pointer group relative"
      >
        <div
          className="h-full bg-gradient-to-r from-brand-orange to-brand-red rounded-full relative transition-all"
          style={{ width: `${progress}%` }}
        >
          <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-brand-muted font-mono w-24">
          {fmt(currentTime)} / {fmt(duration)}
        </span>

        <div className="flex items-center gap-3">
          {/* Rewind 15s */}
          <button
            onClick={() => skip(-15)}
            className="text-brand-muted hover:text-white transition-colors"
            aria-label="Rewind 15 seconds"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M11.99 5V1l-5 5 5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6h-2c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8zm-1.1 11h-.85v-3.26l-1.01.31v-.69l1.77-.63h.09V16zm4.28-1.76c0 .32-.03.6-.1.82s-.17.42-.29.57-.28.26-.45.33-.37.1-.59.1-.41-.03-.59-.1-.33-.18-.46-.33-.23-.34-.3-.57-.11-.5-.11-.82c0-.32.04-.6.11-.82s.17-.42.3-.57.28-.26.46-.33.37-.1.59-.1.41.03.59.1.33.18.45.33.23.34.29.57.1.5.1.82zm-.74 0c0-.19-.01-.35-.04-.48s-.07-.23-.12-.31-.11-.14-.19-.17-.16-.05-.25-.05-.18.02-.25.05-.14.09-.19.17-.09.18-.12.31-.04.29-.04.48c0 .19.01.35.04.48s.07.24.12.32.11.14.19.17.16.05.25.05.18-.02.25-.05.14-.09.19-.17.09-.19.12-.32.04-.29.04-.48z" />
            </svg>
          </button>

          {/* Play/Pause */}
          <button
            onClick={togglePlay}
            className="w-12 h-12 rounded-full bg-gradient-to-br from-brand-orange to-brand-red flex items-center justify-center hover:scale-105 active:scale-95 transition-transform shadow-lg shadow-brand-orange/20"
            aria-label={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? (
              <svg viewBox="0 0 24 24" fill="white" className="w-5 h-5">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="white" className="w-5 h-5 ml-0.5">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>

          {/* Forward 30s */}
          <button
            onClick={() => skip(30)}
            className="text-brand-muted hover:text-white transition-colors"
            aria-label="Forward 30 seconds"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M18 13c0 3.31-2.69 6-6 6s-6-2.69-6-6 2.69-6 6-6v4l5-5-5-5v4c-4.42 0-8 3.58-8 8s3.58 8 8 8 8-3.58 8-8h-2zm-7.46 3h-.85v-3.26l-1.01.31v-.69l1.77-.63h.09V16zm4.28-1.76c0 .32-.03.6-.1.82s-.17.42-.29.57-.28.26-.45.33-.37.1-.59.1-.41-.03-.59-.1-.33-.18-.46-.33-.23-.34-.3-.57-.11-.5-.11-.82c0-.32.04-.6.11-.82s.17-.42.3-.57.28-.26.46-.33.37-.1.59-.1.41.03.59.1.33.18.45.33.23.34.29.57.1.5.1.82zm-.74 0c0-.19-.01-.35-.04-.48s-.07-.23-.12-.31-.11-.14-.19-.17-.16-.05-.25-.05-.18.02-.25.05-.14.09-.19.17-.09.18-.12.31-.04.29-.04.48c0 .19.01.35.04.48s.07.24.12.32.11.14.19.17.16.05.25.05.18-.02.25-.05.14-.09.19-.17.09-.19.12-.32.04-.29.04-.48z" />
            </svg>
          </button>
        </div>

        <div className="flex items-center gap-3 w-24 justify-end">
          {/* Speed */}
          <button
            onClick={cycleSpeed}
            className="text-xs font-mono text-brand-muted hover:text-white transition-colors px-2 py-1 rounded bg-white/5 hover:bg-white/10"
          >
            {SPEEDS[speedIdx]}x
          </button>

          {/* Download */}
          <a
            href={src}
            download
            className="text-brand-muted hover:text-white transition-colors"
            aria-label="Download episode"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
              <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}

function fmt(seconds: number): string {
  if (!seconds || !isFinite(seconds)) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}
