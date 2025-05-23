# Voice-to-Voice Sleep Coaching Agent

This project implements an intelligent voice-to-voice sleep coaching agent that provides personalized sleep advice and guidance using OpenAI's GPT-4 and voice capabilities.

## Features

- Voice input and output for natural conversation
- Sleep-specific knowledge base
- Evidence-based sleep advice
- Conversation history tracking
- Real-time audio processing

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Microphone and speakers

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the sleep coaching agent:
```bash
python sleep_coach.py
```

The agent will:
1. Record your voice input
2. Transcribe it to text
3. Generate a sleep-coaching response
4. Convert the response to speech

To end the conversation, say "quit", "exit", or "bye".

## Example Conversations

The agent is specialized in handling queries about:
- Sleep stages and their importance
- Sleep hygiene best practices
- Common sleep issues and solutions
- Sleep schedule optimization
- Sleep environment recommendations

## Note

This agent uses OpenAI's GPT-4 model and requires an active internet connection to function. The quality of responses depends on the clarity of voice input and the specificity of questions asked. 