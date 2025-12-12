
const logContainer = document.getElementById('log-container');

function log(message, type = 'system') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    const now = new Date();
    const timeStr = now.toLocaleTimeString();

    entry.innerHTML = `
        <span class="timestamp">${timeStr}</span>
        <span class="content">${message}</span>
    `;

    logContainer.prepend(entry);
}

async function sendCommand(action) {
    log(`Sending command: ${action}...`, 'outbound');

    try {
        const response = await fetch('/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: action,
                data: { "timestamp": Date.now() }
            })
        });

        const result = await response.json();

        if (result.status === 'success') {
            log(`Command sent successfully.`, 'system');
        } else {
            log(`Error sending command: ${result.message}`, 'system');
        }
    } catch (error) {
        log(`Network Error: ${error.message}`, 'system');
    }
}

async function pollMessages() {
    try {
        const response = await fetch('/api/poll');
        const data = await response.json();

        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                const contentStr = typeof msg.content === 'object'
                    ? JSON.stringify(msg.content, null, 2)
                    : msg.content;

                log(`[${msg.sender}] ${msg.action}: ${contentStr}`, 'inbound');
            });
        }
    } catch (error) {
        console.error('Polling error:', error);
    }
}

// Start polling every 2 seconds
setInterval(pollMessages, 2000);
