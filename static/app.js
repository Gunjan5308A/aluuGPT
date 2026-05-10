const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

let currentTheme = localStorage.getItem('theme') || 'dark';
html.setAttribute('data-theme', currentTheme);
updateThemeText();

// --- Theme Logic ---
themeToggle.addEventListener('click', () => {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeText();
});

function updateThemeText() {
    themeToggle.innerText = currentTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Pitch Black Mode';
}

// --- Textarea Logic ---
function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
}

// --- Token Logic ---
const activeTokens = new Set();
function toggleToken(btn) {
    const token = btn.getAttribute('data-token');
    if (activeTokens.has(token)) {
        activeTokens.delete(token);
        btn.classList.remove('active');
    } else {
        activeTokens.add(token);
        btn.classList.add('active');
    }
}

// --- Chat Logic ---
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text && activeTokens.size === 0) return;

    // Construct message with tokens
    let fullMessage = text;
    activeTokens.forEach(t => {
        if (!fullMessage.includes(t)) {
            fullMessage += ` ${t}`;
        }
    });

    appendMessage('user', fullMessage);
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Clear active tokens UI
    document.querySelectorAll('.token-btn').forEach(btn => btn.classList.remove('active'));
    const tokensToSend = Array.from(activeTokens);
    activeTokens.clear();

    // Show Loading
    const loadingId = appendLoading();

    try {
        // Handle normal chat
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: fullMessage })
        });
        const data = await response.json();
        
        removeLoading(loadingId);
        appendMessage('ai', data.response);

        // Handle animation if token was present
        if (tokensToSend.includes('[animation]')) {
            const animLoadingId = appendLoading('Generating Animation...');
            try {
                const animResponse = await fetch('/generate_animation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: text })
                });
                const animData = await animResponse.json();
                removeLoading(animLoadingId);
                
                if (animData.video_url) {
                    appendVideo(animData.video_url);
                } else if (animData.detail) {
                    appendMessage('ai', `Animation Error: ${animData.detail}`);
                } else {
                    appendMessage('ai', 'Animation failed without a specific error.');
                }
            } catch (err) {
                removeLoading(animLoadingId);
                appendMessage('ai', 'Failed to connect for animation generation.');
            }
        }

    } catch (error) {
        console.error(error);
        removeLoading(loadingId);
        appendMessage('ai', 'Error connecting to the server. Please check your .env configuration.');
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// --- UI Helpers ---
function appendMessage(role, text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper';
    
    // Hide technical tokens from the UI
    let cleanText = text.replace(/<\|?think\|?>.*?<\/\|?think\|?>/gs, '');
    cleanText = cleanText.replace(/<\|?think\|?>/g, '');
    cleanText = cleanText.replace(/<\|?fast\|?>/g, '');
    cleanText = cleanText.replace(/\[animation\]/g, '');
    cleanText = cleanText.trim();
    
    if (!cleanText && role === 'user') {
        // If it was just a token, show a placeholder or just return
        cleanText = "Token Action Triggered";
    }

    const msg = document.createElement('div');
    msg.className = `message ${role}`;
    
    // Parse Markdown if role is AI, or just use text if user (to avoid XSS if we want, 
    // but usually AI output needs parsing)
    if (typeof marked !== 'undefined') {
        msg.innerHTML = marked.parse(cleanText);
    } else {
        msg.innerText = cleanText;
    }
    
    wrapper.appendChild(msg);
    chatMessages.appendChild(wrapper);

    // Render LaTeX if KaTeX is available
    if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(msg, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError : false
        });
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendLoading(text = '') {
    const id = 'loading-' + Date.now();
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper';
    wrapper.id = id;
    
    const loading = document.createElement('div');
    loading.className = 'message ai';
    loading.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="loading-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            ${text ? `<span style="font-size: 0.8rem; opacity: 0.6;">${text}</span>` : ''}
        </div>
    `;
    
    wrapper.appendChild(loading);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function appendVideo(url) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper';
    
    const container = document.createElement('div');
    container.className = 'video-container';
    
    const video = document.createElement('video');
    video.src = url;
    video.controls = true;
    video.autoplay = true;
    
    container.appendChild(video);
    wrapper.appendChild(container);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function createNewChat() {
    chatMessages.innerHTML = `
        <div class="message-wrapper">
            <div class="message ai">
                New session started. How can I assist?
            </div>
        </div>
    `;
}
