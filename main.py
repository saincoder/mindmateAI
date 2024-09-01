import os
import streamlit as st
from gtts import gTTS
from io import BytesIO
from groq import Groq, APITimeoutError, APIConnectionError

# Initialize the Groq client with the API key from the environment
client = Groq(api_key='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')

# Function to read the prompt from the text file for the chatbot interaction
def load_prompt(filename):
    with open(filename, 'r') as file:
        return file.read()

# Function to read the prompt for the prescription generation
def load_pre(filename):
    with open(filename, 'r') as file:
        return file.read()

# Load the prompt from the text file
prescription_prompt = load_pre('mindmate_prescription_prompt.txt')
prompt_content = load_prompt('mindmate_chat_prompt.txt')

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to sanitize input
def sanitize_input(user_input):
    return user_input.replace("<", "&lt;").replace(">", "&gt;")

# Function to generate a prescription based on various factors
def generate_prescription(mood, symptoms_str, behaviors, medication_preference, additional_info):
    mood = sanitize_input(mood)
    symptoms = sanitize_input(symptoms_str)
    behaviors = sanitize_input(behaviors)
    medication_preference = sanitize_input(medication_preference)
    additional_info = sanitize_input(additional_info)

    prompt = (f"Patient has reported the following details:\n"
              f"Mood: {mood}\n"
              f"Symptoms: {symptoms}\n"
              f"Behaviors: {behaviors}\n"
              f"Medication required: {medication_preference}. "
              f"Additional Information: {additional_info}\n"
              f"Provide a prescription based on the above details.")

    retries = 3  # Number of times to retry the request
    delay = 5    # Delay in seconds between retries

    while retries > 0:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prescription_prompt},
                    {"role": "user", "content": prompt}  # Using 'system' for instructions
                ],
                model="llama3-8b-8192"
            )
            prescription_text = chat_completion.choices[0].message.content
            play_voice(prescription_text)  # Add TTS for the prescription
            return prescription_text
        except (APITimeoutError, APIConnectionError) as e:
            retries -= 1
            st.error(f"Error: {str(e)}. Retrying...")
            if retries == 0:
                return f"Error: {str(e)}. Please try again later."

# Function to interact with the bot
def chat_with_bot(user_message, user_history=None):
    user_message = sanitize_input(user_message)
    history = user_history if user_history else ""
    prompt = f"User history: {history}\nUser message: {user_message}"

    retries = 3
    delay = 5

    while retries > 0:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_content},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-70b-versatile"
            )
            bot_response = chat_completion.choices[0].message.content
            play_voice(bot_response)  # Add TTS for the bot's response
            return bot_response
        except (APITimeoutError, APIConnectionError) as e:
            retries -= 1
            st.error(f"Error: {str(e)}. Retrying...")
            if retries == 0:
                return f"Error: {str(e)}. Please try again later."

# Function to convert text to speech and play it
def play_voice(text):
    tts = gTTS(text=text, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)  # Reset buffer position
    st.audio(audio_bytes, format='audio/mp3')

# Main function to run the Streamlit app
def main():
    # display an image from the local directory
    image_path = "MM221.jpg"  # Replace with your local image path
    st.image(image_path, use_column_width=80,)

    # Sidebar for Track Symptoms
    with st.sidebar:
        st.header("Track Symptoms")
        mood = st.selectbox("Select your mood", [
            "Happy", "Sad", "Anxious", "Angry", "Neutral"
        ])
        
        # Display mood-specific symptoms
        if mood == "Happy":
            symptoms = st.multiselect("Select your symptoms", ["Excitement", "High energy", "Optimism"])
        elif mood == "Sad":
            symptoms = st.multiselect("Select your symptoms", ["Fatigue", "Hopelessness", "Crying spells"])
        elif mood == "Anxious":
            symptoms = st.multiselect("Select your symptoms", ["Restlessness", "Palpitations", "Sweating"])
        elif mood == "Angry":
            symptoms = st.multiselect("Select your symptoms", ["Irritability", "Outbursts", "Tension"])
        else:
            symptoms = st.multiselect("Select your symptoms", ["Calm", "Indifference", "No strong feelings"])

        behaviors = st.text_input("Describe your behaviors")
        medication_preference = st.selectbox("Do you want medication in the prescription?", ["Select", "Yes", "No"])
        additional_info = st.text_area("Additional Information (optional)")

        symptoms_str = ", ".join(symptoms)
        if st.button("Get Prescription"):
            if symptoms_str:
                prescription = generate_prescription(mood, symptoms_str, behaviors, medication_preference, additional_info)
                st.session_state['chat_history'].append(f"Prescription: {prescription}")
                st.markdown("[Chat with the doctor](#chat-with-bot)")
            else:
                st.error("Please select at least one symptom.")

    # Main area for Chat with Bot
    st.header("Chat with MindMate")
    user_message = st.text_input("Your message:")
    if st.button("Send Message"):
        if user_message:
            bot_response = chat_with_bot(user_message)
            st.session_state['chat_history'].append(f"User: {user_message}")
            st.session_state['chat_history'].append(f"Bot: {bot_response}")
        else:
            st.error("Please enter a message.")

    # Custom CSS for message bubbles with user and bot icons, and prescription background
    st.markdown("""
        <style>
        .user-bubble {
            display: flex;
            justify-content: flex-end;
            align-items: start;
            margin-bottom: 10px;
        }
        .user-icon {
            background-color: #8964c7;
            border-radius: 50%;
            margin-right: 10px;
        }
        .user-text {
            background-color: #8964c7;
            padding: 10px;
            border-radius: 15px;
            max-width: 70%;
            text-align: right;
        }
        .bot-bubble {
            display: flex;
            justify-content: flex-start;
            align-items: start;
            margin-bottom: 10px;
        }
        .bot-icon {
            background-color: #8964c7;
            border-radius: 50%;
            margin-right: 10px;
        }
        .bot-text {
            background-color: #8964c7;
            padding: 10px;
            border-radius: 15px;
            max-width: 70%;
            text-align: left;
        }
        .prescription {
            background-color: #E6F7FF;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            color: #004085;
            border: 1px solid #B8DAFF;
        }
        </style>
        """, unsafe_allow_html=True)

    # Display chat history with bubble UI and icons, including prescription style
    user_icon_url = "https://img.icons8.com/?size=100&id=108652&format=png&color=000000"  # Replace with actual icon URL
    bot_icon_url = "https://img.icons8.com/?size=100&id=45060&format=png&color=000000"  # Replace with actual icon URL

    for i, message in enumerate(st.session_state['chat_history']):
        if message.startswith("User:"):
            st.markdown(f"""
                <div class="user-bubble">
                    <img src="{user_icon_url}" class="user-icon" width="30px" height="30px" />
                    <div class="user-text">{message.replace('User:', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        elif message.startswith("Prescription:"):
            st.markdown(f"""
                <div class="prescription">
                    {message.replace('Prescription:', '')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="bot-bubble">
                    <img src="{bot_icon_url}" class="bot-icon" width="30px" height="30px" />
                    <div class="bot-text">{message.replace('Bot:', '')}</div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
