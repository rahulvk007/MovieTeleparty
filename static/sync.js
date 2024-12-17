function startSync(video, syncUrl, role, sessionCode) {
    console.log(`[DEBUG] Role: ${role}, Session Code: ${sessionCode}`);

    // Poll every 2 seconds for better synchronization
    setInterval(() => {
        const data = {
            session_code: sessionCode,
            role: role,
            position: video.currentTime,
            paused: video.paused
        };

        fetch(syncUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(syncData => {
            console.log(`[DEBUG] Received Sync Data -> Position: ${syncData.position}, Paused: ${syncData.paused}`);

            if (role === "friend") {
                // Adjust video position if it deviates by more than 1 second
                if (Math.abs(video.currentTime - syncData.position) > 1) {
                    console.log(`[DEBUG] Adjusting Position -> Current: ${video.currentTime}, Target: ${syncData.position}`);
                    video.currentTime = syncData.position;
                }

                // Adjust playback state
                if (syncData.paused && !video.paused) {
                    console.log("[DEBUG] Pausing video");
                    video.pause();
                } else if (!syncData.paused && video.paused) {
                    console.log("[DEBUG] Playing video");
                    video.play();
                }
            }
        })
        .catch(error => console.error("Sync Error:", error));
    }, 2000);
}
