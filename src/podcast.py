import wave
from pathlib import Path
from google import genai
from google.genai import types


DIALOGUE_PROMPT = """You are a scriptwriter for a weekly Databricks podcast called "Databricks Weekly{track_suffix}".
Two hosts discuss the week's most important {track_intro} developments.

HOSTS:
- {host1_name}: {host1_role}
- {host2_name}: {host2_role}

RULES:
- This episode covers {track_intro}
- Write a natural, conversational dialogue -- NOT a formal news broadcast
- {host1_name} tends to explain the technical significance of things
- {host2_name} asks the questions a real practitioner would ask: "Can we use this today?", "Does this replace X?", "What does this mean for our migration?"
- Include natural reactions: "Oh that's actually huge", "Wait, really?", "OK so basically..."
- Don't cover everything -- pick the 4-5 most interesting topics and go deeper
- Start with a quick intro mentioning this is the {track_intro} edition, end with a brief sign-off
- Target approximately {target_words} words
- Format each line as: SpeakerName: dialogue text

IMPORTANT: Use EXACTLY these speaker names: "{host1_name}" and "{host2_name}" (the TTS engine maps voices to these names)

---
DIGEST CONTENT:

{digest}
"""


class PodcastGenerator:

    def __init__(
        self,
        api_key: str,
        host1_name: str = "Amir",
        host1_voice: str = "Kore",
        host1_role: str = "The knowledgeable host",
        host2_name: str = "Dana",
        host2_voice: str = "Puck",
        host2_role: str = "The curious co-host",
        tts_model: str = "gemini-2.5-flash-preview-tts",
        text_model: str = "gemini-2.5-flash",
        target_words: int = 1800,
    ):
        self.client = genai.Client(api_key=api_key)
        self.host1_name = host1_name
        self.host1_voice = host1_voice
        self.host1_role = host1_role
        self.host2_name = host2_name
        self.host2_voice = host2_voice
        self.host2_role = host2_role
        self.tts_model = tts_model
        self.text_model = text_model
        self.target_words = target_words

    def generate(
        self,
        digest: str,
        output_dir: Path,
        file_suffix: str = "",
        track_name: str = "",
        track_intro: str = "the latest Databricks developments",
    ) -> dict:
        output_dir.mkdir(parents=True, exist_ok=True)
        label = track_name or "General"

        print(f"  [{label}] Generating podcast dialogue...")
        dialogue = self._generate_dialogue(digest, track_name, track_intro)
        dialogue_path = output_dir / f"podcast_script{file_suffix}.txt"
        dialogue_path.write_text(dialogue, encoding="utf-8")
        print(f"  [{label}] Script saved ({len(dialogue.split())} words)")

        print(f"  [{label}] Rendering audio with Gemini TTS...")
        audio_path = self._render_audio(dialogue, output_dir, file_suffix)
        print(f"  [{label}] Audio saved: {audio_path}")

        return {
            "dialogue_path": str(dialogue_path),
            "audio_path": str(audio_path),
            "word_count": len(dialogue.split()),
        }

    def _generate_dialogue(
        self, digest: str, track_name: str, track_intro: str,
    ) -> str:
        track_suffix = f": {track_name}" if track_name else ""

        prompt = DIALOGUE_PROMPT.format(
            track_suffix=track_suffix,
            track_intro=track_intro,
            host1_name=self.host1_name,
            host1_role=self.host1_role,
            host2_name=self.host2_name,
            host2_role=self.host2_role,
            target_words=self.target_words,
            digest=digest,
        )

        response = self.client.models.generate_content(
            model=self.text_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=8000,
            ),
        )

        return response.text

    def _render_audio(self, dialogue: str, output_dir: Path, file_suffix: str = "") -> Path:
        word_count = len(dialogue.split())
        chunk_limit = 6000

        if word_count <= chunk_limit:
            audio_data = self._tts_call(dialogue)
        else:
            audio_data = self._tts_chunked(dialogue, chunk_limit)

        audio_path = output_dir / f"podcast{file_suffix}.wav"
        self._save_wav(audio_path, audio_data)
        return audio_path

    def _tts_call(self, text: str) -> bytes:
        tts_prompt = f"TTS the following conversation between {self.host1_name} and {self.host2_name}:\n\n{text}"

        response = self.client.models.generate_content(
            model=self.tts_model,
            contents=tts_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker=self.host1_name,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=self.host1_voice,
                                    )
                                ),
                            ),
                            types.SpeakerVoiceConfig(
                                speaker=self.host2_name,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=self.host2_voice,
                                    )
                                ),
                            ),
                        ]
                    )
                ),
            ),
        )

        return response.candidates[0].content.parts[0].inline_data.data

    def _tts_chunked(self, dialogue: str, chunk_limit: int) -> bytes:
        lines = dialogue.split("\n")
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_words = 0

        for line in lines:
            line_words = len(line.split())
            if current_words + line_words > chunk_limit and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_words = 0
            current_chunk.append(line)
            current_words += line_words

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        print(f"  Dialogue split into {len(chunks)} audio chunks")
        all_audio = b""
        for i, chunk in enumerate(chunks):
            print(f"  Rendering chunk {i + 1}/{len(chunks)}...")
            all_audio += self._tts_call(chunk)

        return all_audio

    @staticmethod
    def _save_wav(path: Path, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm_data)
