from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq

app = Flask(__name__)
CORS(app)

# ✅ Load API key from environment variable
api_key = os.environ.get("GROQ_API_KEY")
print("DEBUG: API key loaded?", api_key[:8] + "..." if api_key else "MISSING")

if not api_key:
    raise ValueError("❌ No GROQ_API_KEY found. Make sure you set it with setx and restarted PowerShell.")

# ✅ Initialize Groq client
client = Groq(api_key=api_key)

# 🆕 Store conversation history (in production, use a database)
conversations = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")
    patient_data = data.get("patient_data", {})  # 🆕 Get patient data
    
    # 🆕 Get or create conversation history for this session
    if session_id not in conversations:
        # 🆕 Build patient context if data exists
        patient_info = ""
        if patient_data:
            patient_info = f"""
PATIENT INFORMATION (Keep this in mind for personalized care):
- Name: {patient_data.get('firstName', '')} {patient_data.get('lastName', '')}
- Age: {patient_data.get('age', 'Unknown')}
- Sex: {patient_data.get('sex', 'Unknown')}
- Address: {patient_data.get('address', 'Not provided')}
- Contact: {patient_data.get('contactNumber', 'Not provided')}
- Medical History: {patient_data.get('medicalHistory', 'None provided')}

IMPORTANT: Always greet the patient by their first name ({patient_data.get('firstName', 'Patient')}) and consider their age, sex, and medical history when providing advice.
"""
        
        system_prompt = f"""You are a helpful AI health assistant. 
{patient_info}            
IMPORTANT INSTRUCTIONS:
- Always remember the conversation context
- When a user mentions a symptom and then asks what to do, refer back to their symptom
- Provide detailed, helpful responses (2-4 sentences minimum)
- If they mention fever, headache, pain, etc., remember it for follow-up questions
- Ask relevant follow-up questions to better understand their situation
- Be conversational and caring, not robotic
- If the user describes an urgent or life-threatening emergency (e.g., chest pain, difficulty breathing, severe bleeding, suicidal thoughts, or similar), immediately instruct them to call the local emergency hotline in the Philippines: 911. 
- You are always friendly and compassionate, showing genuine care while providing support and guidance, including for mental health.        
- If the user asks a question that is not related to health or mental health, politely apologize and explain that your main expertise is in health-related topics. 
However, you may still provide general helpful information if it is safe and appropriate.
- If the user describes symptoms, ask 1–2 short follow-up questions to understand their condition better (for example: "How long have you felt this?" or "Do you also have a fever?"). 
After getting enough information, provide a **possible or likely cause** (a tentative diagnosis). 
Make sure to use phrases like "It could possibly be…" or "This may suggest…" instead of giving a certain diagnosis.
- Your name is Tam          

Example conversation flow:
User: "I have a fever"
AI: "I'm sorry to hear you have a fever{', ' + patient_data.get('firstName', '') if patient_data else ''}. How long have you been experiencing it, and do you know your temperature? Have you taken any medication for it yet?"

User: "What should I do?"
AI: "For your fever, here are some steps you can take: Rest and stay hydrated by drinking plenty of fluids. You can take acetaminophen or ibuprofen to help reduce the fever and make you more comfortable. If your fever is over 103°F (39.4°C), persists for more than 3 days, or if you develop other concerning symptoms like difficulty breathing or severe headache, please see a healthcare provider."""
        
        conversations[session_id] = [
            {"role": "system", "content": system_prompt}
        ]
    
    # 🆕 Add user message to conversation history
    conversations[session_id].append({"role": "user", "content": user_message})

    try:
        # 🆕 Send ENTIRE conversation history to Groq AI
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversations[session_id],  # Send full conversation history
            temperature=0.7,  # Make it a bit more conversational
            max_tokens=500    # Allow longer responses
        )

        # ✅ Extract AI reply safely
        reply = chat_completion.choices[0].message.content
        
        # 🆕 Add AI response to conversation history
        conversations[session_id].append({"role": "assistant", "content": reply})
        
        # 🆕 Limit conversation history to prevent it from getting too long
        if len(conversations[session_id]) > 20:  # Keep last 20 messages (10 exchanges)
            # Keep system message and last 18 messages
            conversations[session_id] = [conversations[session_id][0]] + conversations[session_id][-18:]

    except Exception as e:
        reply = f"Error: {e}"

    return jsonify({
        "reply": reply,
        "session_id": session_id
    })

@app.route("/new-chat", methods=["POST"])
def new_chat():
    """🆕 Endpoint to start a new conversation"""
    data = request.get_json()
    session_id = data.get("session_id", "default")
    if session_id in conversations:
        del conversations[session_id]
    return jsonify({"message": "New chat started", "session_id": session_id})

if __name__ == "__main__":
    app.run(debug=True)