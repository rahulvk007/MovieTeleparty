function startSync(video, syncUrl, role, sessionCode) {
    console.log(`[DEBUG] Role: ${role}, Session Code: ${sessionCode}`);

    // Poll every 1 second
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
            if (role === "friend") {
                if (Math.abs(video.currentTime - syncData.position) > 1) {
                    video.currentTime = syncData.position;
                }
                if (syncData.paused && !video.paused) {
                    video.pause();
                } else if (!syncData.paused && video.paused) {
                    video.play();
                }
            }
        })
        .catch(error => console.error("Sync Error:", error));
    }, 1000);
}
