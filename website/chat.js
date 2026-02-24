// Atlantiplex AI Chat Widget
// Connects to local Ollama instance

let aiChatOpen = false;
let isProcessing = false;

document.addEventListener('DOMContentLoaded', function() {
    checkAIStatus();
});

/**
 * Check Ollama connection status
 */
async function checkAIStatus() {
    const statusDot = document.getElementById('ai-status-dot');
    const statusText = document.getElementById('ai-status-text');
    
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'connected') {
            statusDot.classList.remove('disconnected');
            statusText.textContent = 'Connected';
        } else {
            statusDot.classList.add('disconnected');
            statusText.textContent = 'Disconnected';
        }
    } catch (error) {
        statusDot.classList.add('disconnected');
        statusText.textContent = 'Offline';
    }
}

/**
 * Toggle AI chat visibility
 */
function toggleAIChat() {
    const chatContainer = document.getElementById('ai-chat');
    const chatToggle = document.getElementById('ai-chat-toggle');
    
    aiChatOpen = !aiChatOpen;
    
    if (aiChatOpen) {
        chatContainer.classList.add('active');
        document.getElementById('ai-input').focus();
    } else {
        chatContainer.classList.remove('active');
    }
}

/**
 * Handle Enter key in chat input
 */
function handleAIKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendAIMessage();
    }
    
    // Auto-resize textarea
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
}

/**
 * Send a quick prompt from buttons
 */
function sendQuickPrompt(prompt) {
    const input = document.getElementById('ai-input');
    input.value = prompt;
    sendAIMessage();
}

/**
 * Send message to AI
 */
async function sendAIMessage() {
    if (isProcessing) return;
    
    const input = document.getElementById('ai-input');
    const sendBtn = document.getElementById('ai-send-btn');
    const chatToggle = document.getElementById('ai-chat-toggle');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Show user message
    addMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    // Show processing state
    isProcessing = true;
    chatToggle.classList.add('processing');
    sendBtn.disabled = true;
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (data.error) {
            addMessage(`🌊 Apologies, I'm having trouble connecting to the deep. Error: ${data.error}`, 'error');
        } else {
            addMessage(data.response, 'ai');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('🌊 The currents are too strong. Please try again later.', 'error');
        console.error('AI Chat error:', error);
    }
    
    // Reset processing state
    isProcessing = false;
    chatToggle.classList.remove('processing');
    sendBtn.disabled = false;
    
    // Scroll to bottom
    const messagesContainer = document.getElementById('ai-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Add message to chat
 */
function addMessage(text, type) {
    const messagesContainer = document.getElementById('ai-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-message ${type}`;
    
    const avatar = type === 'ai' ? '🤖' : '👤';
    messageDiv.innerHTML = `<span class="ai-message-avatar">${avatar}</span>${text}`;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const messagesContainer = document.getElementById('ai-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'ai-typing-indicator ai-message ai';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return 'typing-indicator';
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}
