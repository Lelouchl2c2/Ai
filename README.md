# Lilith Local AI (Ollama)

Yes — the installer installs the model.

## Where safety rules are
Safety is currently enforced in these places:
1. `Modelfile` system prompt safety section (blocks harmful/illegal/explicit sexual content).
2. `chat.py` `BASE_SYSTEM` prompt line that repeats safety constraints in every request.
3. `presets/emotion_presets.json` where `horny` exists but is marked `blocked`.
4. `chat.py` `normalize_emotion_key()` remaps blocked moods to neutral.

## Command palette (+)
Type `+` in chat to open a small expandable command palette, then press a number to auto-send that command.

## Main commands
- `/list`
- `/persona <name>`
- `/model <name>`
- `/clean`
- `/memory-clear`
- `/quit`
- `+` open command palette
