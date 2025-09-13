import streamlit as st
import random
import time
from datetime import datetime
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Configure page
st.set_page_config(
    page_title="AI-Powered Interview Chatbot",
    layout="wide"
)

# Initialize session state
if 'conversation_state' not in st.session_state:
    st.session_state.conversation_state = 'greeting'
if 'candidate_data' not in st.session_state:
    st.session_state.candidate_data = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = []
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = None

# Load AI model for question generation
@st.cache_resource
def load_ai_model():
    """Load a lightweight AI model for question generation"""
    try:
        # Using GPT-2 small for better performance on M2 MacBook
        model_name = "gpt2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Set pad token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create text generation pipeline
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=200,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )
        return generator
    except Exception as e:
        st.error(f"Error loading AI model: {e}")
        return None

# Enhanced question templates (fallback)
QUESTION_TEMPLATES = {
    'python': [
        "Hello! Let's start with Python. Can you explain the difference between lists and tuples in Python? When would you use each?",
        "Great! Now, how do you handle exceptions in Python? Can you walk me through a try-except block example?",
        "Interesting! What are Python decorators? Can you show me how to create a custom decorator?",
        "Excellent! Explain the concept of list comprehensions. Can you write a comprehension that filters even numbers?",
        "Perfect! How does Python's garbage collection work? What are some memory management best practices you follow?"
    ],
    'mysql': [
        "Hello! Let's discuss databases. Can you explain the difference between INNER JOIN and LEFT JOIN? When would you use each?",
        "Good! What are database indexes? How do they improve query performance in MySQL?",
        "Nice! Explain database normalization. What are the different normal forms and why are they important?",
        "Excellent! What are stored procedures in MySQL? When would you use them over regular queries?",
        "Great! How do you optimize a slow-running MySQL query? What tools and techniques do you use?"
    ],
    'nlp': [
        "Hello! Let's talk about NLP. Can you explain the difference between stemming and lemmatization?",
        "Interesting! What are word embeddings? How do Word2Vec and GloVe differ in their approaches?",
        "Great! Explain the concept of TF-IDF. How is it calculated and when would you use it?",
        "Excellent! What are n-grams? How do you choose the right n-gram size for different tasks?",
        "Perfect! Explain sentiment analysis. What approaches would you use for different types of text?"
    ],
    'javascript': [
        "Hello! Let's start with JavaScript. Can you explain the difference between var, let, and const?",
        "Good! What are closures in JavaScript? Can you provide a practical example of how you'd use them?",
        "Interesting! How does the event loop work in JavaScript? Can you explain the call stack?",
        "Great! Explain promises and async/await. How do they differ from traditional callbacks?",
        "Excellent! What are the differences between == and === in JavaScript? Why is this important?"
    ],
    'react': [
        "Hello! Let's discuss React. Can you explain the component lifecycle? What are the key lifecycle methods?",
        "Good! What are React hooks? Can you compare useState and useEffect with examples?",
        "Interesting! How do you manage state in React applications? What's your approach?",
        "Great! Explain the difference between props and state in React. When do you use each?",
        "Excellent! What is the Virtual DOM? How does React's reconciliation process work?"
    ],
    'aws': [
        "Hello! Let's talk about AWS. Can you explain the difference between EC2 and Lambda services? When would you use each?",
        "Good! How would you design a scalable web application on AWS? What services would you include?",
        "Interesting! What are the different storage options in AWS? Compare S3, EBS, and EFS.",
        "Great! Explain auto-scaling in AWS. How do you configure it for different scenarios?",
        "Excellent! How do you ensure security in AWS applications? What services and best practices do you use?"
    ],
    'java': [
        "Hello! Let's discuss Java. Can you explain the main concepts of object-oriented programming in Java?",
        "Good! What's the difference between abstract classes and interfaces in Java? When would you use each?",
        "Interesting! How does garbage collection work in Java? What are the different GC algorithms?",
        "Great! Explain multithreading in Java. How do you handle thread safety in your applications?",
        "Excellent! What are design patterns in Java? Can you explain the Singleton pattern and its use cases?"
    ],
    'sql': [
        "Hello! Let's talk about SQL. Can you explain the difference between INNER JOIN and LEFT JOIN? When would you use each?",
        "Good! What are database indexes? How do they improve query performance?",
        "Interesting! Explain database normalization. What are the different normal forms?",
        "Great! What are stored procedures? When would you use them over regular queries?",
        "Excellent! How do you optimize a slow-running SQL query? What's your systematic approach?"
    ],
    'general': [
        "Hello! Let's start with a general question. Can you walk me through a challenging project you've worked on? What made it difficult?",
        "Interesting! How do you approach debugging a complex issue? What's your systematic process?",
        "Great! Explain your experience with version control. How do you manage code collaboration in a team?",
        "Good! What's your approach to code testing? How do you ensure quality in your projects?",
        "Excellent! How do you stay updated with the latest developments in your field? What resources do you use?"
    ]
}

def detect_greeting(text):
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
    return any(greeting in text.lower() for greeting in greetings)

def detect_ending(text):
    endings = ['bye', 'goodbye', 'thank you', 'thanks', 'see you', 'see ya', 'farewell', 'end', 'quit', 'exit']
    return any(ending in text.lower() for ending in endings)

def generate_ai_questions(tech_stack, years_experience, job_role, ai_model):
    """Generate questions using AI model based on candidate profile"""
    if not ai_model:
        return get_questions_for_tech_stack(tech_stack)
    
    try:
        # Create a detailed prompt based on candidate profile
        prompt = f"""Generate 5 technical interview questions for a candidate with:
- Technical Stack: {tech_stack}
- Years of Experience: {years_experience}
- Job Role: {job_role}

Create diverse, practical questions that match their experience level. Make them conversational and interview-appropriate.

Questions:"""
        
        # Generate questions using AI
        response = ai_model(
            prompt,
            max_length=400,
            num_return_sequences=1,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            pad_token_id=ai_model.tokenizer.eos_token_id
        )
        
        generated_text = response[0]['generated_text']
        
        # Extract questions from generated text
        questions = []
        lines = generated_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and '?' in line and not line.startswith(prompt.split('\n')[0]):
                # Clean up the question
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    questions.append(line)
                elif not any(q in line.lower() for q in ['generate', 'questions', 'candidate', 'technical', 'interview']):
                    if len(questions) < 5:
                        questions.append(f"{len(questions) + 1}. {line}")
        
        # If we don't have enough questions, fill with template questions
        if len(questions) < 5:
            template_questions = get_questions_for_tech_stack(tech_stack)
            for i, tq in enumerate(template_questions):
                if len(questions) < 5:
                    questions.append(tq)
        
        return questions[:5]
        
    except Exception as e:
        st.error(f"Error generating AI questions: {e}")
        return get_questions_for_tech_stack(tech_stack)

def get_questions_for_tech_stack(tech_stack):
    """Get questions based on tech stack (fallback method)"""
    tech_stack_lower = tech_stack.lower()
    
    # Find matching tech stacks
    matched_stacks = ['general']
    for key in QUESTION_TEMPLATES:
        if key != 'general' and key in tech_stack_lower:
            matched_stacks.append(key)
    
    # Collect questions from matched stacks
    all_questions = []
    for stack in matched_stacks:
        all_questions.extend(QUESTION_TEMPLATES[stack])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_questions = []
    for q in all_questions:
        if q not in seen:
            seen.add(q)
            unique_questions.append(q)
    
    # Randomly select 5 questions
    if len(unique_questions) >= 5:
        selected = random.sample(unique_questions, 5)
    else:
        selected = unique_questions
    
    return selected

def add_message(sender, message, message_type="normal"):
    """Add a message to chat history"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        'sender': sender,
        'message': message,
        'type': message_type
    })

def display_chat():
    """Display the chat interface"""
    st.markdown("### 💬 Interview Chat")
    st.markdown("---")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['sender'] == 'Bot':
                with st.chat_message("assistant"):
                    st.write(f"**Bot:** {msg['message']}")
            else:
                with st.chat_message("user"):
                    st.write(f"**You:** {msg['message']}")
                   

def start_interview():
    """Start the interview process"""
    st.session_state.interview_started = True
    st.session_state.current_question = 0
    
    # Load AI model if not already loaded
    if st.session_state.ai_model is None:
        with st.spinner("Loading AI model for personalized questions..."):
            st.session_state.ai_model = load_ai_model()
    
    # Generate questions using AI model
    with st.spinner("Generating personalized interview questions..."):
        st.session_state.interview_questions = generate_ai_questions(
            st.session_state.candidate_data['tech_stack'],
            st.session_state.candidate_data['years_experience'],
            st.session_state.candidate_data['job_role'],
            st.session_state.ai_model
        )
    
    # Add welcome message
    welcome_msg = f"Hello {st.session_state.candidate_data['name']}! I'm your AI interview assistant. I've generated personalized questions based on your {st.session_state.candidate_data['years_experience']} years of experience as a {st.session_state.candidate_data['job_role']} with expertise in {st.session_state.candidate_data['tech_stack']}. Let's begin!"
    add_message('Bot', welcome_msg)
    
    # Add first question
    if st.session_state.interview_questions:
        add_message('Bot', st.session_state.interview_questions[0])
        st.session_state.current_question = 1

def next_question():
    """Move to the next question"""
    if st.session_state.current_question < len(st.session_state.interview_questions):
        add_message('Bot', st.session_state.interview_questions[st.session_state.current_question])
        st.session_state.current_question += 1
    else:
        # Interview completed
        add_message('Bot', "Thank you for the interview! That was the last question. You did great! Do you have any questions for me?")
        st.session_state.conversation_state = 'interview_completed'

def main():
    st.title("HireBuddy 🫂✨")
    st.markdown("Welcome! I'm your AI interview assistant. I'll conduct a personalized, real-time interview with you using advanced AI to generate questions tailored to your experience and role.")
    
    # Sidebar for candidate info
    with st.sidebar:
        st.markdown("## 👤 Candidate Information")
        if st.session_state.candidate_data:
            st.write(f"**Name:** {st.session_state.candidate_data.get('name', 'N/A')}")
            st.write(f"**Email:** {st.session_state.candidate_data.get('email', 'N/A')}")
            st.write(f"**Phone:** {st.session_state.candidate_data.get('phone', 'N/A')}")
            st.write(f"**Experience:** {st.session_state.candidate_data.get('years_experience', 'N/A')}")
            st.write(f"**Job Role:** {st.session_state.candidate_data.get('job_role', 'N/A')}")
            st.write(f"**Tech Stack:** {st.session_state.candidate_data.get('tech_stack', 'N/A')}")
        
        st.markdown("## Interview Progress")
        if st.session_state.interview_started and st.session_state.interview_questions:
            progress = st.session_state.current_question / len(st.session_state.interview_questions)
            st.progress(progress)
            st.write(f"Question {st.session_state.current_question} of {len(st.session_state.interview_questions)}")
        
        st.markdown("## Instructions")
        st.markdown("""
        1. **Fill in your details** below (including experience & role)
        2. **Start the interview** when ready
        3. **Answer questions** in the chat
        4. **Type your responses** naturally
        5. **Ask questions** if you have any
        """)
    
    # Main content area
    if st.session_state.conversation_state == 'greeting':
        st.markdown("**Bot:** Hello! I'm your AI interview assistant. Let me get some basic information about you first.")
        
        # Candidate information form
        with st.form("candidate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Your Name", placeholder="Enter your name")
                email = st.text_input("Email Address", placeholder="Enter your email")
                years_experience = st.selectbox(
                    "Years of Experience",
                    ["0-1 years", "1-2 years", "2-3 years", "3-5 years", "5-7 years", "7-10 years", "10+ years"],
                    help="Select your professional experience level"
                )
            
            with col2:
                phone = st.text_input("Phone Number", placeholder="Enter your phone")
                job_role = st.selectbox(
                    "Job Role",
                    ["Software Developer", "Senior Developer", "Tech Lead", "Data Scientist", "ML Engineer", 
                     "DevOps Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer",
                     "Database Administrator", "System Administrator", "Other"],
                    help="Select your current or target job role"
                )
                tech_stack = st.text_input("Technical Stack", placeholder="e.g., Python, MySQL, NLP")
            
            # Custom job role input
            if job_role == "Other":
                custom_role = st.text_input("Specify your job role", placeholder="Enter your specific job role")
                if custom_role:
                    job_role = custom_role
            
            submitted = st.form_submit_button("Start Interview", type="primary")
            
            if submitted:
                if name and email and phone and tech_stack and years_experience and job_role:
                    st.session_state.candidate_data = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'tech_stack': tech_stack,
                        'years_experience': years_experience,
                        'job_role': job_role
                    }
                    st.session_state.conversation_state = 'interview_ready'
                    st.rerun()
                else:
                    st.error("Please fill in all fields!")
    
    elif st.session_state.conversation_state == 'interview_ready':
        st.markdown(f"**Bot:** Perfect! I have your information. I'll be conducting a personalized interview for a **{st.session_state.candidate_data.get('job_role', 'N/A')}** position, tailored to your **{st.session_state.candidate_data.get('years_experience', 'N/A')}** experience level with **{st.session_state.candidate_data.get('tech_stack', 'N/A')}**. Are you ready to start?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Start Interview!", type="primary"):
                start_interview()
                st.session_state.conversation_state = 'interviewing'
                st.rerun()
        
        with col2:
            if st.button("Let me review my info", type="secondary"):
                st.session_state.conversation_state = 'greeting'
                st.rerun()
    
    elif st.session_state.conversation_state == 'interviewing':
        # Display chat
        display_chat()
        
        # Chat input
        st.markdown("---")
        user_input = st.chat_input("Type your answer here...")
        
        if user_input:
            # Add user message
            add_message('You', user_input)
            
            # Check for ending keywords
            if detect_ending(user_input):
                add_message('Bot', "I understand you'd like to end the interview. Thank you for your time!")
                st.session_state.conversation_state = 'interview_completed'
                st.rerun()
            else:
                # Move to next question
                if st.session_state.current_question < len(st.session_state.interview_questions):
                    # Add acknowledgment
                    acknowledgments = [
                        "Thank you for that answer!",
                        "Interesting perspective!",
                        "Good point!",
                        "That's helpful!",
                        "Thanks for explaining that!"
                    ]
                    add_message('Bot', random.choice(acknowledgments))
                    
                    # Add next question
                    next_question()
                else:
                    add_message('Bot', "That was the last question! Thank you for the interview.")
                    st.session_state.conversation_state = 'interview_completed'
            
            st.rerun()
    
    elif st.session_state.conversation_state == 'interview_completed':
        display_chat()
        
        st.markdown("---")
        st.markdown("**Bot:** The interview is complete! Thank you for your time and answers.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Start New Interview", type="primary"):
                # Reset everything
                st.session_state.conversation_state = 'greeting'
                st.session_state.candidate_data = {}
                st.session_state.chat_history = []
                st.session_state.current_question = 0
                st.session_state.interview_questions = []
                st.session_state.interview_started = False
                st.session_state.ai_model = None
                st.rerun()
        
        with col2:
            if st.button("Review Answers", type="secondary"):
                st.markdown("### 📝 Interview Summary")
                st.write("Here's a summary of your interview:")
                for i, msg in enumerate(st.session_state.chat_history):
                    if msg['sender'] == 'Bot' and '?' in msg['message']:
                        st.write(f"**Q{i+1}:** {msg['message']}")
        
        with col3:
            if st.button("End Session", type="secondary"):
                st.markdown("**Bot:** Thank you! Goodbye and good luck! 👋")
                st.stop()

if __name__ == "__main__":
    main()
