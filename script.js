document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  // 🆕 Get patient data from localStorage
  const patientData = JSON.parse(localStorage.getItem('patientData'));
  
  // 🆕 If no patient data, redirect to form
  if (!patientData) {
    window.location.href = 'form.html';
    return;
  }

  // 🆕 Generate a unique session ID for this chat session
  let sessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

  // 🆕 Add a "New Chat" button
  const header = document.querySelector('h2');
  const newChatBtn = document.createElement('button');
  newChatBtn.textContent = 'New Chat';
  newChatBtn.className = 'new-chat-btn';
  newChatBtn.onclick = startNewChat;
  header.parentNode.insertBefore(newChatBtn, header.nextSibling);

  // 🆕 Add a "New Patient" button
  const newPatientBtn = document.createElement('button');
  newPatientBtn.textContent = 'New Patient';
  newPatientBtn.className = 'new-chat-btn';
  newPatientBtn.style.marginLeft = '10px';
  newPatientBtn.onclick = () => {
    if (confirm('Register a new patient? Current chat will be lost.')) {
      localStorage.removeItem('patientData');
      window.location.href = 'form.html';
    }
  };
  header.parentNode.insertBefore(newPatientBtn, header.nextSibling);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userMessage = input.value.trim();
    if (!userMessage) return;

    // 🆕 Show user message with better styling
    addMessage(userMessage, 'user');
    input.value = "";

    // 🆕 Show typing indicator
    const typingId = showTypingIndicator();

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: sessionId,
          patient_data: patientData  // 🆕 Send patient data
        })
      });

      const data = await response.json();
      
      // Remove typing indicator
      removeTypingIndicator(typingId);
      
      // 🚨 Check if this is an emergency
      if (data.is_emergency) {
        showEmergencyAlert();
      }
      
      // Show AI response
      addMessage(data.reply, 'bot');
      
    } catch (error) {
      removeTypingIndicator(typingId);
      addMessage(`Error: ${error.message}`, 'error');
    }
  });

  // 🆕 Function to add messages with proper styling
  function addMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    if (type === 'user') {
      messageDiv.innerHTML = `<div class="message-label">You</div><div class="message-text">${escapeHtml(message)}</div>`;
    } else if (type === 'bot') {
      // Format AI message with proper line breaks
      const formattedMessage = formatAIMessage(message);
      messageDiv.innerHTML = `<div class="message-label">AI Health Assistant (Tam)</div><div class="message-text">${formattedMessage}</div>`;
    } else if (type === 'error') {
      messageDiv.innerHTML = `<div class="message-label">Error</div><div class="message-text">${escapeHtml(message)}</div>`;
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // 🆕 Format AI messages for better readability
  function formatAIMessage(message) {
    // Escape HTML first
    message = escapeHtml(message);
    
    // Convert line breaks to <br>
    message = message.replace(/\n/g, '<br>');
    
    // Make bullet points more visible
    message = message.replace(/^- /gm, '• ');
    message = message.replace(/^\* /gm, '• ');
    
    // Make numbered lists more visible
    message = message.replace(/^(\d+)\./gm, '<strong>$1.</strong>');
    
    return message;
  }

  // 🆕 Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // 🆕 Show typing indicator
  function showTypingIndicator() {
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

  // 🆕 Remove typing indicator
  function removeTypingIndicator(typingElement) {
    if (typingElement && typingElement.parentNode) {
      typingElement.parentNode.removeChild(typingElement);
    }
  }

  // 🆕 Start a new chat conversation
  async function startNewChat() {
    try {
      // First, tell server to delete old conversation
      const oldSessionId = sessionId;
      
      await fetch("http://127.0.0.1:5000/new-chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ session_id: oldSessionId })
      });
      
      // 🔥 Generate a NEW session ID AFTER deleting old one
      sessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      
      console.log("New chat started with session:", sessionId);
      
      // Clear chat box
      chatBox.innerHTML = '';
      
      // Show welcome message with patient name
      addMessage(`Hello ${patientData.firstName}! I'm your AI health assistant, My name is Tam. How can I help you today?`, 'bot');
      
    } catch (error) {
      console.error('Error starting new chat:', error);
      addMessage("Error starting new chat. Please refresh the page.", 'error');
    }
  }

  // 🆕 Show initial welcome message with patient name
  addMessage(`Hello ${patientData.firstName}! I'm your AI health assistant, My name is Tam. How can I help you today?`, 'bot');

  // 🚨 Function to show emergency alert with hotlines
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
    
    // Play alert sound (optional - browser may block)
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYKFmW57eeiUBELUKXi77dmHQU3jdLux3AfBi15yfDbizcIGGG07tqaTxAMT6Pd8Lpjnkg');
      audio.volume = 0.3;
      audio.play().catch(() => {});
    } catch(e) {}
  }
});