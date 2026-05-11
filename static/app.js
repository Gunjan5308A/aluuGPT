const chatMessages = document.getElementById('chatMessages');
const historyList = document.getElementById('historyList');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const themeToggle = document.getElementById('themeToggle');
const authModal = document.getElementById('authModal');
const authModalBackdrop = document.getElementById('authModalBackdrop');
const authModalClose = document.getElementById('authModalClose');
const authUsername = document.getElementById('authUsername');
const authPassword = document.getElementById('authPassword');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const authError = document.getElementById('authError');
const authToggleBtn = document.getElementById('authToggleBtn');
const accountStatus = document.getElementById('accountStatus');
const inputContainer = document.querySelector('.input-container');
const html = document.documentElement;

let currentTheme = localStorage.getItem('theme') || 'dark';
let currentUser = null;

html.setAttribute('data-theme', currentTheme);
updateThemeText();
setComposerLocked(true);

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

// --- Auth Logic ---
async function apiFetch(url, options = {}) {
    const config = {
        credentials: 'include',
        ...options,
        headers: {
            ...(options.headers || {})
        }
    };

    if (options.body && !config.headers['Content-Type']) {
        config.headers['Content-Type'] = 'application/json';
    }

    return fetch(url, config);
}

function setComposerLocked(locked) {
    userInput.disabled = locked;
    sendBtn.disabled = locked;
    inputContainer.classList.toggle('is-locked', locked);
    userInput.placeholder = locked ? 'Log in to start chatting' : 'Ask anything... (Use tokens for specific modes)';
}

function setAuthError(message = '') {
    authError.textContent = message;
}

function openAuthModal() {
    authModal.hidden = false;
    setAuthError('');
    authUsername.focus();
}

function closeAuthModal() {
    authModal.hidden = true;
    setAuthError('');
}

function setLoggedOutView() {
    currentUser = null;
    authToggleBtn.textContent = 'Login';
    accountStatus.hidden = true;
    accountStatus.textContent = '';
    setComposerLocked(true);
    renderWelcomeMessage();
    closeAuthModal();
}

function setLoggedInView(user) {
    currentUser = user;
    authToggleBtn.textContent = 'Logout';
    accountStatus.hidden = false;
    accountStatus.textContent = user.username;
    setComposerLocked(false);
    closeAuthModal();
}

async function submitAuth(action) {
    setAuthError('');
    const username = authUsername.value.trim();
    const password = authPassword.value;

    if (!username || !password) {
        setAuthError('Enter both username and password.');
        return;
    }

    try {
        const response = await apiFetch(`/auth/${action}`, {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (!response.ok) {
            setAuthError(data.detail || 'Authentication failed.');
            return;
        }

        authPassword.value = '';
        setLoggedInView(data.user);
        await loadHistory();
    } catch (error) {
        console.error(error);
        setAuthError('Could not reach the server.');
    }
}

loginBtn.addEventListener('click', () => submitAuth('login'));
registerBtn.addEventListener('click', () => submitAuth('register'));

authToggleBtn.addEventListener('click', async () => {
    if (!currentUser) {
        openAuthModal();
        return;
    }

    try {
        await apiFetch('/auth/logout', { method: 'POST' });
    } catch (error) {
        console.error(error);
    }
    authUsername.value = '';
    authPassword.value = '';
    setAuthError('');
    setLoggedOutView();
});

authModalBackdrop.addEventListener('click', closeAuthModal);
authModalClose.addEventListener('click', closeAuthModal);

authPassword.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        submitAuth('login');
    }
});

authUsername.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        submitAuth('login');
    }
});

authModal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeAuthModal();
    }
});

async function loadAuthState() {
    try {
        const response = await apiFetch('/auth/me', { method: 'GET' });
        const data = await response.json();
        if (data.authenticated) {
            setLoggedInView(data.user);
            await loadHistory();
            return;
        }
    } catch (error) {
        console.error(error);
    }
    setLoggedOutView();
}

async function loadHistory() {
    if (!currentUser) {
        return;
    }

    try {
        const response = await apiFetch('/history', { method: 'GET' });
        const data = await response.json();
        if (!response.ok) {
            if (response.status === 401) {
                handleUnauthorized('Your session expired. Please log in again.');
            }
            return;
        }

        renderConversation(data.messages || []);
        renderHistoryList(data.messages || []);
    } catch (error) {
        console.error(error);
    }
}

function handleUnauthorized(message) {
    setAuthError(message || 'Login required.');
    setLoggedOutView();
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
    if (!currentUser) {
        setAuthError('Please log in before sending a message.');
        return;
    }

    const text = userInput.value.trim();
    if (!text && activeTokens.size === 0) return;

    let fullMessage = text;
    activeTokens.forEach(t => {
        if (!fullMessage.includes(t)) {
            fullMessage += ` ${t}`;
        }
    });

    appendMessage('user', fullMessage);
    userInput.value = '';
    userInput.style.height = 'auto';

    document.querySelectorAll('.token-btn').forEach(btn => btn.classList.remove('active'));
    const tokensToSend = Array.from(activeTokens);
    activeTokens.clear();

    const loadingId = appendLoading();

    try {
        const response = await apiFetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message: fullMessage })
        });
        const data = await response.json();

        removeLoading(loadingId);

        if (!response.ok) {
            if (response.status === 401) {
                handleUnauthorized(data.detail || 'Login required.');
            } else {
                appendMessage('ai', data.detail || 'Something went wrong.');
            }
            return;
        }

        appendMessage('ai', data.response);

        if (tokensToSend.includes('[animation]')) {
            const animLoadingId = appendLoading('Generating Animation...');
            try {
                const animResponse = await apiFetch('/generate_animation', {
                    method: 'POST',
                    body: JSON.stringify({ prompt: text })
                });
                const animData = await animResponse.json();
                removeLoading(animLoadingId);

                if (!animResponse.ok) {
                    if (animResponse.status === 401) {
                        handleUnauthorized(animData.detail || 'Login required.');
                    } else if (animData.video_url) {
                        appendVideo(animData.video_url);
                    } else {
                        appendMessage('ai', animData.detail || 'Animation failed without a specific error.');
                    }
                    return;
                }

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
        appendMessage('ai', 'Error connecting to the server. Please check your environment configuration.');
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
function escapeText(text) {
    const span = document.createElement('span');
    span.textContent = text;
    return span.innerHTML;
}

function renderWelcomeMessage() {
    chatMessages.innerHTML = `
        <div class="message-wrapper">
            <div class="message ai">
                Log in to load your personal chat history and continue your workspace.
            </div>
        </div>
    `;
    historyList.innerHTML = '';
}

function renderConversation(messages) {
    chatMessages.innerHTML = '';

    if (!messages.length) {
        chatMessages.innerHTML = `
            <div class="message-wrapper">
                <div class="message ai">
                    Hello. How can I assist your workflow today?
                </div>
            </div>
        `;
        return;
    }

    messages.forEach((message) => {
        appendMessage(message.role, message.content, false);
    });
}

function renderHistoryList(messages) {
    historyList.innerHTML = '';

    if (!messages.length) {
        const empty = document.createElement('div');
        empty.style.opacity = '0.6';
        empty.style.fontSize = '0.85rem';
        empty.style.lineHeight = '1.5';
        empty.textContent = 'No saved messages yet.';
        historyList.appendChild(empty);
        return;
    }

    messages.slice(-8).reverse().forEach((message) => {
        const item = document.createElement('div');
        item.style.border = '1px solid var(--border-color)';
        item.style.borderRadius = '0.7rem';
        item.style.padding = '0.65rem 0.75rem';
        item.style.marginBottom = '0.5rem';
        item.style.fontSize = '0.82rem';
        item.style.lineHeight = '1.45';
        item.style.opacity = '0.9';
        item.textContent = `${message.role === 'user' ? 'You' : 'AI'}: ${message.content.slice(0, 80)}${message.content.length > 80 ? '...' : ''}`;
        historyList.appendChild(item);
    });
}

function appendMessage(role, text, shouldScroll = true) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper';

    let cleanText = String(text || '')
        .replace(/<\|?think\|?>.*?<\/\|?think\|?>/gs, '')
        .replace(/<\|?think\|?>/g, '')
        .replace(/<\|?fast\|?>/g, '')
        .replace(/\[animation\]/g, '')
        .trim();

    if (!cleanText && role === 'user') {
        cleanText = 'Token Action Triggered';
    }

    const msg = document.createElement('div');
    msg.className = `message ${role}`;

    if (role === 'user') {
        msg.textContent = cleanText;
    } else if (typeof marked !== 'undefined') {
        msg.innerHTML = marked.parse(cleanText);
    } else {
        msg.textContent = cleanText;
    }

    wrapper.appendChild(msg);
    chatMessages.appendChild(wrapper);

    if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(msg, {
            delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '$', right: '$', display: false },
                { left: '\\(', right: '\\)', display: false },
                { left: '\\[', right: '\\]', display: true }
            ],
            throwOnError: false
        });
    }

    if (shouldScroll) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
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
            ${text ? `<span style="font-size: 0.8rem; opacity: 0.6;">${escapeText(text)}</span>` : ''}
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
    activeTokens.clear();
    document.querySelectorAll('.token-btn').forEach(btn => btn.classList.remove('active'));
    if (currentUser) {
        chatMessages.innerHTML = `
            <div class="message-wrapper">
                <div class="message ai">
                    New session started. How can I assist?
                </div>
            </div>
        `;
    } else {
        renderWelcomeMessage();
    }
}

loadAuthState();
