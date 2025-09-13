# Hiring Assistant Bot

A simple Streamlit chatbot that generates interview questions based on a candidate's technical stack. Optimized for MacBook M2 Air with lightweight AI models.

## Features

- 🤖 Interactive chatbot interface
- 📝 Candidate information collection (name, email, phone, tech stack)
- 🎯 AI-generated interview questions tailored to technical expertise
- 💬 Greeting and conversation handling
- 🚀 Lightweight model optimized for M2 MacBook Air

## Installation

1. Clone or download this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Interactive Chatbot (advanced_chatbot.py) - **RECOMMENDED**
Real-time conversational interview with smart follow-up questions:
```bash
streamlit run advanced_chatbot.py
```

### Option 2: Basic Chatbot (chatbot_app.py) - Simple Conversation
Basic interactive interview chatbot:
```bash
streamlit run chatbot_app.py
```

### Option 3: Question Generator (app_improved.py) - Just Questions
Generates and displays questions without conversation:
```bash
streamlit run app_improved.py
```

### Option 4: Optimized Version (app_optimized.py) - Fast & Lightweight
Template-based question generation for instant performance:
```bash
streamlit run app_optimized.py
```

### Option 5: Original AI Version (app.py) - Legacy
Uses Microsoft DialoGPT-small (may have repetition issues):
```bash
streamlit run app.py
```

2. Open your browser and navigate to the provided local URL (usually `http://localhost:8501`)

3. Follow the on-screen instructions:
   - Fill in candidate details
   - Click "Generate Interview Questions"
   - Review the generated questions
   - End the conversation when done

## Technical Details

- **Framework**: Streamlit
- **AI Models**: 
  - **Improved**: GPT-2 with enhanced templates (recommended)
  - **Optimized**: Template-based (fastest)
  - **Legacy**: Microsoft DialoGPT-small
- **Platform**: Optimized for MacBook M2 Air
- **Dependencies**: See `requirements.txt`

## Recent Improvements (v3.0)

- ✅ **Interactive Chatbots**: Real-time conversational interviews
- ✅ **Smart Follow-ups**: AI analyzes responses and asks relevant follow-up questions
- ✅ **Progress Tracking**: Visual progress bar and question counter
- ✅ **Answer Storage**: Saves all candidate responses
- ✅ **Download Summary**: Export complete interview results
- ✅ **Response Analysis**: AI evaluates answer quality and depth
- ✅ **Natural Flow**: Conversational interview experience
- ✅ **Fixed Repetition Issue**: No more duplicate questions
- ✅ **Better AI Model**: GPT-2 with improved prompting
- ✅ **Enhanced Templates**: 60+ unique questions with follow-ups

## Supported Interactions

### Greetings
- Hi, Hello, Hey
- Good morning, Good afternoon, Good evening
- Greetings

### Endings
- Bye, Goodbye
- Thank you, Thanks
- See you, See ya
- Farewell, End, Quit, Exit

## File Structure

```
hiring_assistant/
├── advanced_chatbot.py # 🤖 INTERACTIVE CHATBOT (Recommended)
├── chatbot_app.py      # Basic conversational chatbot
├── app_improved.py     # Question generator (no chat)
├── app_optimized.py    # Fast template-based version
├── app.py              # Legacy AI version
├── requirements.txt    # Python dependencies
├── test_app.py         # Test script
├── test_improved.py    # Test improved version
├── compare_versions.py # Compare old vs new
├── chatbot_demo.py     # Chatbot demo script
├── demo.py            # Demo script
├── install.sh          # Installation script
└── README.md          # This file
```

## Notes

- The model will be downloaded on first run (may take a few minutes)
- The app uses session state to maintain conversation flow
- Questions are generated based on the provided technical stack
- The interface is responsive and user-friendly
