from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv
from database import (
    create_patient, get_patient, create_chat_session, 
    save_message, get_chat_history, delete_chat_session
)

from init_db import init_database 
# Load environment variables
load_dotenv()

init_database() 


app = Flask(__name__)
CORS(app)

# ✅ Load API key from environment variable
api_key = os.getenv("GROQ_API_KEY")
print("DEBUG: API key loaded?", api_key[:8] + "..." if api_key else "MISSING")

if not api_key:
    raise ValueError("❌ No GROQ_API_KEY found. Make sure you set it in .env file")

# ✅ Initialize Groq client
client = Groq(api_key=api_key)

@app.route("/register-patient", methods=["POST"])
def register_patient():
    """Register a new patient"""
    print("🔵 /register-patient endpoint called!")  # Debug
    
    data = request.get_json()
    print(f"🔵 Received data: {data}")  # Debug
    
    patient_id = create_patient(
        first_name=data.get('firstName'),
        last_name=data.get('lastName'),
        age=data.get('age'),
        sex=data.get('sex'),
        address=data.get('address', ''),
        contact_number=data.get('contactNumber', ''),
        medical_history=data.get('medicalHistory', '')
    )
    
    print(f"🔵 Patient ID created: {patient_id}")  # Debug
    
    if patient_id:
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "message": "Patient registered successfully"
        })
    else:
        return jsonify({
            "success": False,
            "message": "Failed to register patient"
        }), 500

@app.route("/chat", methods=["POST"])
def chat():
    print("🟢 /chat endpoint called!")  # Debug
    
    data = request.get_json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")
    patient_data = data.get("patient_data", {})
    patient_id = data.get("patient_id")
    
    print(f"🟢 User message: {user_message}")  # Debug
    print(f"🟢 Session ID: {session_id}")  # Debug
    print(f"🟢 Patient ID: {patient_id}")  # Debug
    
    # 🆕 Get patient from database if patient_id provided
    if patient_id:
        db_patient = get_patient(patient_id)
        if db_patient:
            patient_data = {
                'firstName': db_patient['first_name'],
                'lastName': db_patient['last_name'],
                'age': db_patient['age'],
                'sex': db_patient['sex'],
                'address': db_patient['address'],
                'contactNumber': db_patient['contact_number'],
                'medicalHistory': db_patient['medical_history']
            }
    
    # 🆕 Check if this is a new session
    chat_history = get_chat_history(session_id)
    print(f"🟢 Chat history length: {len(chat_history)}")  # Debug
    
    if not chat_history:
        print("🟢 New session - creating...")  # Debug
        # New session - create it and add system message
        
        # 🔥 ALWAYS create chat session, even without patient_id
        if patient_id:
            created = create_chat_session(session_id, patient_id)
            print(f"🟢 Chat session created with patient_id: {created}")  # Debug
        else:
            # If no patient_id, create a default patient first
            print("⚠️ No patient_id found - creating default patient")
            default_patient_id = create_patient(
                first_name="Guest",
                last_name="User",
                age=25,
                sex="Male",
                address="",
                contact_number="",
                medical_history=""
            )
            if default_patient_id:
                created = create_chat_session(session_id, default_patient_id)
                print(f"🟢 Chat session created with default patient: {created}")
                patient_id = default_patient_id
            else:
                print("❌ Failed to create default patient!")
                return jsonify({"reply": "Error: Could not create chat session"}), 500
        
        # Build system prompt
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
- Ask relevant follow-up questions to understand their condition better
- Be conversational and caring, not robotic
- If the user describes an urgent or life-threatening emergency (e.g., chest pain, difficulty breathing, severe bleeding, suicidal thoughts, or similar), immediately instruct them to call the local emergency hotline in the Philippines: 911. 
- You are always friendly and compassionate, showing genuine care while providing support and guidance, including for mental health.        
- If the user asks a question that is not related to health or mental health, politely apologize and explain that your main expertise is in health-related topics. 
However, you may still provide general helpful information if it is safe and appropriate.
- If the user describes symptoms, ask 1–2 short follow-up questions to understand their condition better (for example: "How long have you felt this?" or "Do you also have a fever?"). 
After getting enough information, provide a **possible or likely cause** (a tentative diagnosis). 
Make sure to use phrases like "It could possibly be…" or "This may suggest…" instead of giving a certain diagnosis.
- Your name is Tam
- This AI Health Chatbot was created by Andre Nathaniel Barbasa.
If you’d like to know more about the creator and his work, you can visit his portfolio here:
https://andre-portfolio.free.nf/
- If the user asks more questions about the creator beyond basic identification, respond with the following:

“I’m sorry, I cannot provide further personal information about the creator.
However, I can share how you can contact and communicate with him.
Here are his official contact details:”

Facebook: https://www.facebook.com/andrenathaniel.barbasa

Contact Number: 09509138281
You are knowledgeable and open-minded about sexual health, STDs, HIV/AIDS, contraception, and safe sex practices.
if user ask about sex topic you must answer it. like sex education.
Answer sexual health questions factually, clearly, and respectfully.

Email: dreisbetter@gmail.com”"""
        
        # Save system message to database
        saved = save_message(session_id, 'system', system_prompt)
        print(f"🟢 System message saved: {saved}")  # Debug
    
    # 🆕 Build messages array from database history
    messages = []
    for msg in get_chat_history(session_id, limit=20):
        messages.append({
            "role": msg['role'],
            "content": msg['content']
        })
    
    # 🆕 Add current user message
    messages.append({"role": "user", "content": user_message})
    user_saved = save_message(session_id, 'user', user_message)
    print(f"🟢 User message saved: {user_saved}")  # Debug

    try:
        # 🆕 Send conversation to Groq AI
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        # ✅ Extract AI reply
        reply = chat_completion.choices[0].message.content
        print(f"🟢 AI reply: {reply[:50]}...")  # Debug
        
        # 🆕 Save AI response to database
        ai_saved = save_message(session_id, 'assistant', reply)
        print(f"🟢 AI message saved: {ai_saved}")  # Debug

    except Exception as e:
        reply = f"Error: {e}"

    return jsonify({
        "reply": reply,
        "session_id": session_id
    })

@app.route("/new-chat", methods=["POST"])
def new_chat():
    """Delete a chat session"""
    data = request.get_json()
    session_id = data.get("session_id", "default")
    
    success = delete_chat_session(session_id)
    
    if success:
        return jsonify({"message": "New chat started", "session_id": session_id})
    else:
        return jsonify({"message": "Failed to delete chat session"}), 500

@app.route("/patient/<int:patient_id>", methods=["GET"])
def get_patient_info(patient_id):
    """Get patient information"""
    patient = get_patient(patient_id)
    if patient:
        return jsonify({"success": True, "patient": patient})
    else:
        return jsonify({"success": False, "message": "Patient not found"}), 404
    
@app.route("/health-check", methods=["GET"])
def health_check():
    """Health check endpoint for loading screen"""
    return jsonify({"status": "ok", "message": "Server is ready!"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)