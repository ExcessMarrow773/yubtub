
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("upload-form");
    const progressContainer = document.getElementById("progress-container");
    const progressBar = document.getElementById("progress-bar");
    const progressText = document.getElementById("progress-text");
    const progressStatus = document.getElementById("progress-status");
    const submitBtn = document.getElementById("submit-btn");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener("loadstart", function () {
            progressContainer.style.display = "block";
            submitBtn.disabled = true;
            submitBtn.textContent = "Uploading…";
            setProgress(0, "Starting upload…");
        });

        xhr.upload.addEventListener("progress", function (e) {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                setProgress(pct, `Uploading… ${pct}%`);
            }
        });

        xhr.upload.addEventListener("load", function () {
            setProgress(100, "Processing on server…");
        });

        xhr.upload.addEventListener("error", function () {
            setError("Upload failed. Please try again.");
        });

        xhr.addEventListener("load", function () {
            if (xhr.status >= 200 && xhr.status < 400) {
                // Success — follow the server redirect
                if (xhr.responseURL && xhr.responseURL !== window.location.href) {
                    setProgress(100, "Upload complete! Redirecting…");
                    window.location.href = xhr.responseURL;
                } else {
                    // Django re-rendered the form with validation errors
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Submit";
                    progressContainer.style.display = "none";
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(xhr.responseText, "text/html");
                    const newForm = doc.getElementById("upload-form");
                    if (newForm) form.innerHTML = newForm.innerHTML;
                }
            } else {
                setError(`Server error (${xhr.status}). Please try again.`);
            }
        });

        xhr.addEventListener("error", function () {
            setError("Network error. Please check your connection.");
        });

        xhr.open("POST", form.action || window.location.href, true);
        xhr.send(formData);
    });

    function setProgress(pct, message) {
        progressBar.value = pct;
        progressText.textContent = pct + "%";
        progressStatus.textContent = message;
    }

    function setError(message) {
        progressStatus.textContent = message;
        progressText.textContent = "Error";
        submitBtn.disabled = false;
        submitBtn.textContent = "Try Again";
    }
});