document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed"); // Debug: Check if DOMContentLoaded is fired

    const video = document.getElementById('my_video');
    const inputCode = document.getElementById('input_code');
    const streamUrlInput = document.getElementById('stream_url');
    const syncCodeInput = document.getElementById('sync_code');
    const submitCodeBtn = document.getElementById('submit_code');

    let player;
    let isAdmin = false; // You might want to set this based on the URL or response

    // Initialize player if video element exists
    if (video) {
        player = videojs('my_video');
        player.on('loadedmetadata', () => {
            console.log("Video metadata loaded"); // Debug: Check if video metadata is loaded
            syncPlayer(); // Initial sync
        });
    }

    // Function to attach event listeners - Call this after dynamic content update
    function attachEventListeners() {
        console.log("Attaching event listeners"); // Debug: Check if attachEventListeners is called

        const newSubmitCodeBtn = document.getElementById('submit_code');
        if (newSubmitCodeBtn) {
            newSubmitCodeBtn.removeEventListener('click', handleSubmit); // Prevent duplicate listeners
            newSubmitCodeBtn.addEventListener('click', handleSubmit);
        }

        // Reinitialize the video player and its event listeners
        const newVideo = document.getElementById('my_video');
        if (newVideo) {
            player = videojs(newVideo);
            player.on('loadedmetadata', () => {
                console.log("Video metadata loaded (after update)"); // Debug: Check if video metadata is loaded after update
                syncPlayer();
            });
        }
    }

    function handleSubmit() {
        console.log("Submit button clicked"); // Debug: Check if submit button click is detected

        const code = inputCode.value;
        console.log("Input Code:", code); // Debug: Log the input code
        let url = '/';
        let formData = new FormData();

        formData.append('input_code', code);

        // Check if sync_code field exists
        if (syncCodeInput) {
            console.log("Sync code field exists"); // Debug: Check if sync_code field is detected
            formData.append('stream_url', streamUrlInput.value);
            formData.append('sync_code', syncCodeInput.value);
            console.log("Stream URL:", streamUrlInput.value); // Debug: Log the stream URL
            console.log("Sync Code:", syncCodeInput.value); // Debug: Log the sync code
        }

        console.log("Sending POST request to:", url); // Debug: Log the URL being requested

        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log("Response received:", response); // Debug: Log the response object
            if (response.ok) {
                return response.text();
            } else {
                throw new Error('Code submission failed');
            }
        })
        .then(html => {
            console.log("Updating page content"); // Debug: Log before updating page content
            // Update the page content
            document.body.innerHTML = html;

            // Reattach event listeners after updating the page
            attachEventListeners();
        })
        .catch(error => {
            console.error('Error:', error); // Debug: Log any errors
            alert(error.message);
        });
    }

    // Attach the event listener initially
    if (submitCodeBtn) {
        submitCodeBtn.addEventListener('click', handleSubmit);
    }

    function syncPlayer() {
        setInterval(() => {
            if (syncCodeInput) {
                let currentSyncCode = syncCodeInput.value;

                fetch('/sync', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `action=get_state&sync_code=${currentSyncCode}`
                })
                .then(response => response.json())
                .then(data => {
                    if (isAdmin) {
                        // Admin updates others
                        updateVideoState(player.currentTime(), player.paused());
                    } else {
                        // Viewers sync to state
                        if (Math.abs(player.currentTime() - data.current_time) > 2) {
                            player.currentTime(data.current_time);
                        }
                        if (player.paused() !== !data.is_playing) {
                            data.is_playing ? player.play() : player.pause();
                        }
                    }
                });
            }
        }, 5000);

        if (isAdmin) {
            player.on('pause', () => updateVideoState(player.currentTime(), true));
            player.on('play', () => updateVideoState(player.currentTime(), false));
            player.on('seeked', () => updateVideoState(player.currentTime(), player.paused()));
        }
    }

    function updateVideoState(currentTime, isPaused) {
        if (syncCodeInput) {
            let currentSyncCode = syncCodeInput.value;
            let currentInputCode = inputCode.value;

            fetch('/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `action=update_state&current_time=${currentTime}&is_playing=${!isPaused}&sync_code=${currentSyncCode}&input_code=${currentInputCode}`
            })
            .then(response => response.json())
            .then(data => {
                // Handle response if needed
            });
        }
    }
});