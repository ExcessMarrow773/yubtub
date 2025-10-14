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

    fetch('like-video/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("like-response").innerText = data.message;
        if (data.liked || data.alreadyLiked) {
            document.getElementById("like-button").disabled = true;
        }
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

//        document.getElementById("follow-response").innerText = data.message;

        if (status === 200) {
            showToast("success", data.message);
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