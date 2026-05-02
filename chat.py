#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

MODEL = "lilith-local"
BASE_SYSTEM = (
    "Stay in character and be helpful. "
    "Refuse harmful, illegal, or explicit requests and redirect safely."
)

PRESETS_DIR = Path(__file__).parent / "presets"
PERSONALITY_FILE = PRESETS_DIR / "personality_presets.json"
EMOTION_FILE = PRESETS_DIR / "emotion_presets.json"
MEMORY_FILE = Path(__file__).parent / "memory.jsonl"
MAX_MEMORY_TURNS = 12

POSITIVE_CUES = {"love", "thanks", "happy", "great", "amazing", "cute"}
DISTRESS_CUES = {"sad", "hurt", "alone", "anxious", "scared", "depressed", "help"}
RISK_CUES = {"danger", "die", "kill", "self-harm", "suicide", "illegal"}

COMMAND_SHORTCUTS = ["/list", "/persona afton", "/model lilith-local", "/clean", "/memory-clear", "/quit"]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def detect_emotion(user_text: str, emotions: dict, fallback: str) -> str:
    text = user_text.lower()
    if any(cue in text for cue in RISK_CUES) and "worried" in emotions:
        return "worried"
    if any(cue in text for cue in DISTRESS_CUES) and "tender" in emotions:
        return "tender"
    if any(cue in text for cue in POSITIVE_CUES) and "joyful" in emotions:
        return "joyful"
    return fallback




def normalize_emotion_key(emotion_key: str, emotions: dict) -> str:
    item = emotions.get(emotion_key, {})
    if item.get("blocked"):
        return "neutral" if "neutral" in emotions else next(iter(emotions))
    return emotion_key



def load_memory(path: Path, max_turns: int):
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    items = []
    for line in lines[-max_turns:]:
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return items


def append_memory(path: Path, role: str, content: str):
    record = {"ts": datetime.utcnow().isoformat(), "role": role, "content": content}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def memory_to_text(items):
    parts = []
    for item in items:
        role = item.get("role", "user")
        content = item.get("content", "")
        parts.append(f"{role.upper()}: {content}")
    return "\n".join(parts)

def build_prompt(user_text: str, personality: dict, emotion: dict, memory_text: str) -> str:
    sys_prompt = (
        f"{BASE_SYSTEM}\n"
        f"Personality: {personality.get('system', '')}\n"
        f"Emotion style: {emotion.get('style', '')}\n"
        f"Emotion stats: valence={emotion.get('valence', 0)}, arousal={emotion.get('arousal', 0)}\n"
    )
    return f"[SYSTEM]\n{sys_prompt}\n[MEMORY]\n{memory_text}\n[USER]\n{user_text}"


def ask_ollama(prompt: str, model: str) -> str:
    cmd = ["ollama", "run", model, prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except FileNotFoundError:
        return "Ollama is not installed or not in PATH."
    except subprocess.CalledProcessError as e:
        err = e.stderr.strip() or "Unknown Ollama error"
        return f"Model call failed: {err}"




def command_palette() -> str | None:
    print("\n+ Command Palette")
    for i, cmd in enumerate(COMMAND_SHORTCUTS, start=1):
        print(f"  {i}. {cmd}")
    pick = input("Choose number (Enter to cancel): ").strip()
    if not pick:
        return None
    if pick.isdigit():
        idx = int(pick) - 1
        if 0 <= idx < len(COMMAND_SHORTCUTS):
            return COMMAND_SHORTCUTS[idx]
    print("Invalid selection.\n")
    return None

def main() -> int:
    personalities = load_json(PERSONALITY_FILE)
    emotions = load_json(EMOTION_FILE)

    if not personalities or not emotions:
        print("Missing preset files in ./presets")
        return 1

    current_persona = "afton" if "afton" in personalities else next(iter(personalities))
    selected_emotion = "neutral" if "neutral" in emotions else next(iter(emotions))
    auto_emotion = True
    current_model = MODEL

    print(f"Local chat started with model: {current_model}")
    print("Commands: /quit, /list, /persona <name>, /model <name>, /clean, /memory-clear, + (palette)\n")

    while True:
        try:
            user = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return 0

        if not user:
            continue
        if user == "+":
            picked = command_palette()
            if not picked:
                continue
            user = picked
            print(f"Running command: {user}\n")

        if user.lower() in {"/quit", "/exit"}:
            print("Goodbye.")
            return 0
        if user.lower() == "/list":
            print("Personas:")
            for key, val in personalities.items():
                disabled = " [disabled]" if val.get("blocked") else ""
                print(f" - {key}{disabled}: {val.get('description', '')}")
            print("Emotions:")
            for key, val in emotions.items():
                disabled = " [disabled]" if val.get("blocked") else ""
                print(f" - {key}{disabled}: {val.get('description', '')}")
            print()
            continue
        if user.lower() == "/memory-clear":
            if MEMORY_FILE.exists():
                MEMORY_FILE.unlink()
            print("Memory cleared.\n")
            continue
        if user.lower() == "/clean":
            print("Launching interactive cleanup tool (asks before every delete)...\n")
            subprocess.run([sys.executable, "cleanup_files.py"])
            continue
        if user.lower().startswith("/persona "):
            key = user.split(maxsplit=1)[1].strip()
            if key in personalities:
                current_persona = key
                print(f"Switched persona to: {key}\n")
            else:
                print("Unknown persona. Use /list.\n")
            continue
        if user.lower().startswith("/model "):
            key = user.split(maxsplit=1)[1].strip()
            if key:
                current_model = key
                print(f"Switched model to: {key}\n")
            else:
                print("Usage: /model <name>\n")
            continue
        if user.lower().startswith("/emotion "):
            key = user.split(maxsplit=1)[1].strip()
            if key in emotions:
                if emotions[key].get("blocked"):
                    selected_emotion = "neutral" if "neutral" in emotions else next(iter(emotions))
                    print("Mood: disabled -> using neutral.\n")
                else:
                    selected_emotion = key
                    print(f"Switched emotion to: {key}\n")
            else:
                print("Unknown emotion. Use /list.\n")
            continue

        active_emotion_key = detect_emotion(user, emotions, selected_emotion) if auto_emotion else selected_emotion
        active_emotion_key = normalize_emotion_key(active_emotion_key, emotions)
        memory_text = memory_to_text(load_memory(MEMORY_FILE, MAX_MEMORY_TURNS))
        prompt = build_prompt(user, personalities[current_persona], emotions[active_emotion_key], memory_text)
        reply = ask_ollama(prompt, current_model)
        append_memory(MEMORY_FILE, "user", user)
        append_memory(MEMORY_FILE, "assistant", reply)
        print(f"LilithAI[{current_persona}/{active_emotion_key}]> {reply}\n")


if __name__ == "__main__":
    raise SystemExit(main())
