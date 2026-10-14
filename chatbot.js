const chatBtn = document.getElementById('chatBtn');
const chatWindow = document.getElementById('chatWindow');
const closeChatBtn = document.getElementById('closeChatBtn');
const chatInput = document.getElementById('chatInput');
const sendMsgBtn = document.getElementById('sendMsgBtn');
const chatBody = document.getElementById('chatBody');

let isChatOpen = false;
let currentArtistContext = null;

// Toggle Chat Window
chatBtn.addEventListener('click', () => {
    isChatOpen = !isChatOpen;
    chatWindow.classList.toggle('hidden');
    if (isChatOpen) {
        chatInput.focus();
        const artistName = document.getElementById('artistInput').value.trim();
        if (artistName && artistName !== currentArtistContext) {
            currentArtistContext = artistName;
            addBotMessage(`Hi! Ask me anything about ${currentArtistContext}.`);
        } else if (!currentArtistContext) {
            addBotMessage("Hi! You can ask me about any singer, or search for one using the main search bar first!");
        }
    }
});

closeChatBtn.addEventListener('click', () => {
    isChatOpen = false;
    chatWindow.classList.add('hidden');
});

// Send Message
sendMsgBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    addUserMessage(text);
    chatInput.value = '';

    getBotResponse(text);
}

function addUserMessage(text) {
    const div = document.createElement('div');
    div.classList.add('chat-message', 'user-message');
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function addBotMessage(text) {
    const div = document.createElement('div');
    div.classList.add('chat-message', 'bot-message');
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function addBotMessageHTML(htmlContent) {
    const div = document.createElement('div');
    div.classList.add('chat-message', 'bot-message');
    div.innerHTML = htmlContent;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function getBotResponse(userText) {
    const artistName = document.getElementById('artistInput').value.trim();

    addBotMessage("Searching...");

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userText: userText,
                artist: artistName,
                query: artistName ? `${artistName} ${userText}` : userText
            })
        });

        // Remove "Searching..."
        const lastMsg = chatBody.lastElementChild;
        if (lastMsg && lastMsg.textContent === "Searching...") lastMsg.remove();

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.answer) {
            const botReply = `
                ${data.answer}
                <br><br>
                <span style="font-size: 0.8rem; opacity: 0.7;">Source: ${data.source || 'Singer AI'}</span>
            `;
            addBotMessageHTML(botReply);
        } else {
            addBotMessage("I couldn't find an answer for that. Try asking something else!");
        }

    } catch (error) {
        console.error('Chatbot Error:', error);
        const lastMsg = chatBody.lastElementChild;
        if (lastMsg && lastMsg.textContent === "Searching...") lastMsg.remove();

        const searchSubject = artistName ? `${artistName} ${userText}` : userText;
        const googleUrl = `https://www.google.com/search?q=${encodeURIComponent(searchSubject)}`;
        addBotMessageHTML(`
            Couldn't fetch response right now.
            <br>
            <a href="${googleUrl}" target="_blank" style="color: #4ade80; text-decoration: underline;">
                Click here to see search results
            </a>
        `);
    }
}
