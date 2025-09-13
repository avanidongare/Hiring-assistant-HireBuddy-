# HireBuddy - An AI powered Hiring Assistant 

A simple Streamlit chatbot that generates interview questions based on a candidate's technical stack. Optimized for MacBook M2 Air with lightweight AI models.

## Features

- Interactive chatbot interface
- Candidate information collection (name, email, phone, tech stack)
- AI-generated interview questions tailored to technical expertise
- Greeting and conversation handling
- lightweight model

## Installation

1. Clone or download this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
streamlit run chatbot_app.py
```

2. Open your browser and navigate to the provided local URL (usually `http://localhost:8501`)

3. Follow the on-screen instructions:
   - Fill in candidate details
   - Click "Generate Interview Questions"
   - Review the generated questions
   - End the conversation when done


## Notes

- The model will be downloaded on first run (may take a few minutes)
- The app uses session state to maintain conversation flow
- Questions are generated based on the provided technical stack
- The interface is responsive and user-friendly
