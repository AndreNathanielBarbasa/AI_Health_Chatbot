document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const newPatientBtn = document.getElementById("new-patient-btn");
  const newChatBtn = document.getElementById("new-chat-btn");
  const patientInfoEl = document.getElementById("patient-info");

  // 🆕 Get patient data from localStorage
  const patientData = JSON.parse(localStorage.getItem('patientData'));
  const patientId = localStorage.getItem('patient_id');
  
  console.log("Patient Data:", patientData);
  console.log("Patient ID:", patientId);
  
  // 🆕 If no patient data, redirect to form
  if (!patientData) {
    console.log("No patient data found - redirecting to form");
    window.location.href = 'form.html';
    return;
  }

  // 🆕 Generate a unique session ID for this chat session
  let sessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  console.log("Session ID:", sessionId);

  // 🆕 Display patient info in header
  if (patientInfoEl) {
    patientInfoEl.textContent = `Patient: ${patientData.firstName} ${patientData.lastName} | Age: ${patientData.age} | ${patientData.sex}`;
  }

  // 🆕 New Patient button handler
  if (newPatientBtn) {
    newPatientBtn.onclick = () => {
      if (confirm('Register a new patient? Current chat will be lost.')) {
        localStorage.removeItem('patientData');
        localStorage.removeItem('patient_id');
        window.location.href = 'form.html';
      }
    };
  }

  // Form submit handler
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userMessage = input.value.trim();
    if (!userMessage) return;

    console.log("User message:", userMessage);

    // Show user message
    addMessage(userMessage, 'user');
    input.value = "";

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
      console.log("Sending to backend...");
      
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: sessionId,
          patient_data: patientData,
          patient_id: patientId
        })
      });

      console.log("Response received:", response.status);

      const data = await response.json();
      console.log("Data:", data);
      
      // Remove typing indicator
      removeTypingIndicator(typingId);
      
      // Check if this is an emergency
      if (data.is_emergency) {
        showEmergencyAlert();
      }
      
      // Show AI response
      if (data.reply) {
        addMessage(data.reply, 'bot');
      } else {
        addMessage("Sorry, I couldn't get a response. Please try again.", 'error');
      }
      
    } catch (error) {
      console.error("Error:", error);
      removeTypingIndicator(typingId);
      addMessage(`Error: ${error.message}`, 'error');
    }
  });

  // Function to add messages
  function addMessage(message, type) {
    console.log("Adding message:", type, message);
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    if (type === 'user') {
      messageDiv.innerHTML = `<div class="message-label">You</div><div class="message-text">${escapeHtml(message)}</div>`;
    } else if (type === 'bot') {
      const formattedMessage = formatAIMessage(message);
      messageDiv.innerHTML = `<div class="message-label">AI Health Assistant (Tam)</div><div class="message-text">${formattedMessage}</div>`;
    } else if (type === 'error') {
      messageDiv.innerHTML = `<div class="message-label">Error</div><div class="message-text">${escapeHtml(message)}</div>`;
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    console.log("Message added to chatBox");
  }

  // Format AI messages
  function formatAIMessage(message) {
    message = escapeHtml(message);
    message = message.replace(/\n/g, '<br>');
    message = message.replace(/^- /gm, '• ');
    message = message.replace(/^\* /gm, '• ');
    message = message.replace(/^(\d+)\./gm, '<strong>$1.</strong>');
    return message;
  }

  // Escape HTML
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Show typing indicator
  function showTypingIndicator() {
    console.log("Showing typing indicator");
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
      <strong>Tam:</strong> 
      <div class="typing-dots">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return typingDiv;
  }

  // Remove typing indicator
  function removeTypingIndicator(typingElement) {
    if (typingElement && typingElement.parentNode) {
      typingElement.parentNode.removeChild(typingElement);
      console.log("Typing indicator removed");
    }
  }

  // Show emergency alert
  function showEmergencyAlert() {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'emergency-alert';
    alertDiv.innerHTML = `
      <div class="emergency-header">🚨 EMERGENCY DETECTED 🚨</div>
      <div class="emergency-content">
        <p><strong>Call emergency services immediately:</strong></p>
        <div class="hotline-buttons">
          <a href="tel:911" class="hotline-btn emergency-911">
            📞 911
            <span>Emergency Hotline</span>
          </a>
          <a href="tel:117" class="hotline-btn red-cross">
            🏥 117
            <span>Philippine Red Cross</span>
          </a>
          <a href="tel:143" class="hotline-btn">
            💬 143
            <span>DOH Health Line</span>
          </a>
          <a href="tel:8527-7700" class="hotline-btn">
            🚑 8527-7700
            <span>Metro Manila ERUF</span>
          </a>
        </div>
        <p class="emergency-note">⚠️ Tap any number above to call immediately</p>
      </div>
    `;
    
    chatBox.appendChild(alertDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Try to play alert sound
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYKFmW57eeiUBELUKXi77dmHQU3jdLux3AfBi15yfDbizcIGGG07tqaTxAMT6Pd8Lpjnkg');
      audio.volume = 0.3;
      audio.play().catch(() => {});
    } catch(e) {}
  }

  // 🆕 New Chat button handler
if (newChatBtn) {
  newChatBtn.onclick = async () => {
    if (!confirm("Start a new chat? Current conversation will be cleared.")) return;

    try {
      // Tell backend to delete old session
      await fetch("http://127.0.0.1:5000/new-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId })
      });

      // Clear chat UI
      chatBox.innerHTML = "";

      // Create a NEW session ID
      sessionId =
        "chat_" +
        Date.now() +
        "_" +
        Math.random().toString(36).substr(2, 9);

      console.log("New Session ID:", sessionId);

      // Show welcome message again
      addMessage(
        `Hello ${patientData.firstName}! I'm your AI health assistant, Tam. How can I help you today?`,
        "bot"
      );

    } catch (error) {
      console.error("Failed to start new chat:", error);
      alert("Failed to start a new chat. Please try again.");
    }
  };
}


  // Show initial welcome message
  console.log("Showing welcome message");
  addMessage(`Hello ${patientData.firstName}! I'm your AI health assistant, My name is Tam. How can I help you today?`, 'bot');
  console.log("Welcome message should be visible now");
});