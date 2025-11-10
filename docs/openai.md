# OpenAI Python Library Documentation - Audio & Text Processing

## Overview

The OpenAI Python library provides access to OpenAI's API for audio
transcription, text processing, and AI-powered tasks.

## Installation

```bash
pip install openai
```

## Audio Transcription (Whisper)

### Basic Audio Transcription

```python
import openai

client = openai.OpenAI(api_key="your-api-key")

# Transcribe audio file
with open("audio.wav", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="de"  # Optional: specify language
    )

print(transcript.text)
```

### Translation (Audio to English)

```python
# Translate audio to English text
with open("german_audio.wav", "rb") as audio_file:
    translation = client.audio.translations.create(
        model="whisper-1",
        file=audio_file
    )

print(translation.text)  # English text regardless of input language
```

### Advanced Transcription Options

```python
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="de",                    # Language hint
    prompt="Medizinische Fachbegriffe, Diagnose, Behandlung",  # Context prompt
    response_format="json",          # json, text, srt, verbose_json, vtt
    temperature=0.0                  # 0.0 to 1.0, lower = more deterministic
)
```

## Text Processing (Chat Completions)

### Basic Text Correction/Processing

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Du bist ein hilfreicher Assistent für Textkorrektur."},
        {"role": "user", "content": f"Korrigiere folgenden transkribierten Text: {raw_text}"}
    ],
    max_tokens=1000,
    temperature=0.3
)

corrected_text = response.choices[0].message.content
```

### Structured Text Processing

```python
prompt = """
Korrigiere folgenden transkribierten Text:
- Verbessere Grammatik und Interpunktion
- Behalte den originalen Sinn bei
- Mache den Text flüssig lesbar
- Keine zusätzlichen Kommentare

Text: {raw_text}
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,  # Low temperature for consistent corrections
    max_tokens=500
)
```

## Streaming Responses

### Streaming Chat Completions

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Correct this text: " + raw_text}],
    stream=True  # Enable streaming
)

collected_text = ""
for chunk in stream:
    if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
        collected_text += content

print(f"\nFinal text: {collected_text}")
```

## Error Handling

### API Errors

```python
try:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
except openai.APIError as e:
    print(f"OpenAI API error: {e}")
except openai.RateLimitError as e:
    print("Rate limit exceeded, retry later")
    time.sleep(60)
except openai.AuthenticationError as e:
    print("Invalid API key")
```

### Network and Timeout Handling

```python
from openai import OpenAI
import time

client = OpenAI(
    api_key="your-key",
    max_retries=3,
    timeout=30.0
)

def transcribe_with_retry(audio_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            with open(audio_path, "rb") as f:
                return client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    return None
```

## Best Practices

### Audio File Preparation

- **Format**: WAV, MP3, M4A, MP4, MPEG, MPGA, MPA, WAV, WEBM
- **Size limit**: 25 MB
- **Sample rate**: Higher rates improve quality but increase processing time
- **Channels**: Mono preferred for transcription
- **Duration**: Keep under 25 minutes for reliability

### API Key Management

```python
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Cost Optimization

- Use appropriate model sizes (whisper-1 for most cases)
- Batch similar requests
- Cache frequent corrections
- Monitor token usage

### Rate Limiting

- Free tier: 50 requests/minute
- Pay-as-you-go: Higher limits
- Implement exponential backoff for retries
- Monitor usage via OpenAI dashboard

## Model Selection

### Whisper Models

- `whisper-1`: Latest and most accurate (recommended)

### Chat Models for Text Processing

- `gpt-4`: Highest quality corrections
- `gpt-4-turbo`: Good balance of quality and speed
- `gpt-3.5-turbo`: Faster but less accurate

## Response Formats

### Transcription Response

```python
{
    "text": "Transcribed text content"
}
```

### Verbose JSON Response

```python
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="verbose_json"
)

# Contains additional metadata
print(transcript.text)
print(transcript.language)
print(transcript.duration)
```

## Integration Patterns

### Voice Transcriber Workflow

```python
class VoiceTranscriber:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def process_audio(self, audio_path):
        # Step 1: Transcribe
        raw_text = self._transcribe_audio(audio_path)

        # Step 2: Correct text
        corrected_text = self._correct_text(raw_text)

        # Step 3: Return result
        return corrected_text

    def _transcribe_audio(self, audio_path):
        with open(audio_path, "rb") as f:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="de"
            )
        return transcript.text

    def _correct_text(self, raw_text):
        prompt = f"""
        Korrigiere diesen transkribierten Text:
        - Grammatik und Interpunktion verbessern
        - Sinn beibehalten
        - Flüssig lesbar machen

        Text: {raw_text}
        """

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        return response.choices[0].message.content
```

## Monitoring and Logging

### Usage Tracking

```python
# Track API usage
response = client.chat.completions.create(...)
usage = response.usage
print(f"Tokens used: {usage.total_tokens}")
print(f"Prompt tokens: {usage.prompt_tokens}")
print(f"Completion tokens: {usage.completion_tokens}")
```

### Error Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # API call
    transcript = client.audio.transcriptions.create(...)
except Exception as e:
    logger.error(f"Transcription failed: {e}")
    raise
```

## Security Considerations

### API Key Protection

- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly
- Monitor usage for unauthorized access

### Data Privacy

- Audio files are processed by OpenAI's servers
- Temporary files should be deleted after processing
- Consider on-premise alternatives for sensitive data
- Review OpenAI's data retention policies

## Troubleshooting

### Common Issues

**"Invalid file format"**

- Ensure audio file is in supported format
- Check file size (max 25MB)
- Verify file is not corrupted

**"Rate limit exceeded"**

- Implement exponential backoff
- Reduce request frequency
- Upgrade to higher tier if needed

**"Authentication failed"**

- Verify API key is correct
- Check key has sufficient credits
- Ensure key has proper permissions

**Poor transcription quality**

- Use higher quality audio input
- Provide language hints
- Add context prompts for technical terms
- Consider audio preprocessing (noise reduction)

**Text correction issues**

- Adjust temperature (lower = more consistent)
- Improve prompts with specific instructions
- Use larger models for complex corrections
- Consider few-shot examples in prompts
