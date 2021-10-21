window.addEventListener("load", () => {
  const streamDiv = document.getElementById("stream");
  const joinButton = document.getElementById("join");
  async function startStream() {
    const response = await fetch("/stream-token", { method: "POST" });
    const { token, message } = await response.json();
    if (token === null) {
      streamDiv.innerHTML = `<p>${message}</p>`;
      return;
    }
    const player = await Twilio.Live.Player.connect(token, {
      playerWasmAssetsPath: "../static/",
    });
    player.play();
    streamDiv.appendChild(player.videoElement);
  }

  // event listeners
  joinButton.addEventListener("click", startStream);
});
