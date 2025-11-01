// chat.js

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;
    messageInput.value = ''; // 清空输入框

    try {
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        console.log('收到响应时间:', new Date().toISOString());
        console.log('前端收到的响应:', data);
        removeLoadingMessage();

        if (data.has_schedule) {
            displayMessage('bot', data.answer + ' <a href="/calendar" target="_blank">点击查看日程</a>');
            window.open('/calendar', '_blank');
        } else {
            displayMessage('bot', data.answer);
        }
    } catch (error) {
        console.error('Error:', error);
        displayMessage('assistant', '抱歉，发送消息时出现了错误。');
    }
}

function displayMessage(role, content) {
    const chatBox = document.getElementById('chatBox');
    const messageElement = document.createElement('div');
    messageElement.className = role;
    messageElement.textContent = content;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function displayLink(href, text) {
    const chatBox = document.getElementById('chatBox');
    const linkElement = document.createElement('a');
    linkElement.href = href;
    linkElement.textContent = text;
    linkElement.target = '_blank';
    chatBox.appendChild(linkElement);
}