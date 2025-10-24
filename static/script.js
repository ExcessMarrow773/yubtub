function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


function likeVideo() {
    const videoId = document.getElementById("like-button").dataset.videoId;

    fetch('/like-video/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(response => response.json())
    .then(data => {
        showToast("success", data.message);
        document.getElementById("like-button").innerText = data.likes + ":👍";
    });
}

function followUser() {
    const followButton = document.getElementById("follow-button");
    const account = followButton.dataset.account;

    console.log(account);

    fetch('/follow-user/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ account: account })
    })
    .then(response => {
        return response.json().then(data => ({
            status: response.status,
            data: data
        }));
    })
    .then(({ status, data }) => {
        console.log(data);

        if (status === 200) {
            showToast("success", data.message);
            if (data.following === true) {
            	followButton.innerHTML = "Unfollow";
            } else {
            	followButton.innerHTML = "Follow";
            }
            console.log(followButton.innerHTML);
        } else {
            showToast("error", data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast("error", "Something went wrong.");
    });
}


function showToast(type, message, duration = 3000) {
    const toastContainer = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.classList.add('toast', type);

    const toastMessage = document.createElement('span');
    toastMessage.classList.add('toast-message');
    toastMessage.textContent = message;
    toast.appendChild(toastMessage);

    const closeButton = document.createElement('button');
    closeButton.classList.add('toast-close-btn');
    closeButton.textContent = '×';
    closeButton.onclick = () => removeToast(toast);
    toast.appendChild(closeButton);

    toastContainer.appendChild(toast);

    // Show the toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10); // Small delay to allow CSS transition

    // Automatically remove the toast after 'duration'
    const timeoutId = setTimeout(() => {
        removeToast(toast);
    }, duration);

    // Store timeoutId on the toast element for potential clearing
    toast.dataset.timeoutId = timeoutId;
}

function removeToast(toastElement) {
    clearTimeout(toastElement.dataset.timeoutId); // Clear the auto-remove timeout
    toastElement.classList.remove('show');
    // Remove from DOM after transition
    toastElement.addEventListener('transitionend', () => {
        toastElement.remove();
    }, { once: true });
}

window.addEventListener('load', () => {
    const chat = document.querySelector('chat');
    if (chat) {
        chat.scrollTop = chat.scrollHeight;
		chat.scrollTo({
    		top: chat.scrollHeight,
    		behavior: 'smooth'
		});
    }
});


function appendChatMessage(text, direction = 'to') {
    // direction: 'to' (you) or 'from' (other)
    const chatWindow = document.querySelector('chat');
    if (!chatWindow) return;

    // create message element (matches your template's <msg> tag)
    const msgEl = document.createElement('msg');
    msgEl.classList.add(direction);
    msgEl.textContent = text;

    // add timestamp
    const ts = document.createElement('span');
    ts.classList.add('timestamp');
    const now = new Date();
    ts.textContent = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    msgEl.appendChild(ts);

    // append and scroll into view
    chatWindow.appendChild(msgEl);
    // smooth scroll to bottom
    chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
}

function sendMsg() {
    const msgInput = document.getElementById('msg');
    const msgText = msgInput.value;
    const sendButton = document.getElementById('sendButton');
    const chatUser = sendButton.dataset.toUser;

    if (msgText === "") {
        showToast("error", "You cant send an empty message.");
        return;
    }

    appendChatMessage(msgText, 'to');
    msgInput.value = '';

    fetch('/chat/send-message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ msg: msgText, to: chatUser})
    })
    .then(response => response.json().then(data => ({ status: response.status, data: data })))
    .then(({ status, data }) => {
        if (status === 200) {
            showToast("success", "Message sent");
        } else {
            showToast("error", data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast("error", "Something went wrong.");
    });
}