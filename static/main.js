window.addEventListener("load", () => {
  // initialize number of participants with local video.
  // we can have a max of six participants.
  let availableYarn = [1, 2, 3, 4, 5, 6];

  // element identifiers
  const startDiv = document.getElementById("start");
  const identityInput = document.getElementById("identity");
  const joinButton = document.getElementById("join");
  const startStreamButton = document.getElementById("startStream");
  const stopStreamButton = document.getElementById("stopStream");
  const streamingStatus = document.getElementById("streamingStatus");

  async function startStream() {
    const response = await fetch("/start-stream");
    const { message } = await response.json();
    if (message === "success") {
      streamingStatus.innerHTML = "You are streaming";
    }
  }

  async function stopStream() {
    const response = await fetch("/stop-stream");
    const { message } = await response.json();
    if (message === "success") {
      streamingStatus.innerHTML = "You are not streaming";
    }
  }

  // join the video room
  async function connect() {
    startDiv.style.display = "none";
    const response = await fetch("/token", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ identity: identityInput.value }),
    });
    const { token } = await response.json();
    const room = await Twilio.Video.connect(token, {
      video: true,
      audio: false,
    });

    handleConnectedParticipant(room.localParticipant);
    room.participants.forEach(handleConnectedParticipant);
    room.on("participantConnected", handleConnectedParticipant);

    // clean up when someone disconnects
    room.on("participantDisconnected", handleDisconnectedParticipant);
    window.addEventListener("pagehide", () => {
      room.disconnect();
    });
    window.addEventListener("beforeunload", () => {
      room.disconnect();
    });
  }

  function handleConnectedParticipant(participant) {
    findNextAvailableYarn(participant);

    participant.tracks.forEach((trackPublication) => {
      handleTrackPublished(trackPublication, participant);
    });
    participant.on("trackPublished", (trackPublication) => {
      handleTrackPublished(trackPublication, participant);
    });
  }

  function handleTrackPublished(trackPublication, participant) {
    const yarn = document.getElementById(`yarn-${participant.number}`);

    function handleTrackSubscribed(track) {
      yarn.appendChild(track.attach());
    }

    if (trackPublication.track) {
      handleTrackSubscribed(trackPublication.track);
    }
    trackPublication.on("subscribed", handleTrackSubscribed);
  }

  // tidy up helper function for when a participant disconnects
  // or closes the page
  function handleDisconnectedParticipant(participant) {
    participant.removeAllListeners();
    const el = document.getElementById(`yarn-${participant.number}`);
    el.innerHTML = "";
    availableYarn.push(participant.number);
  }

  // helper to find a spot on the page to display participant video
  function findNextAvailableYarn(participant) {
    const index = Math.floor(Math.random() * availableYarn.length);
    const choice = availableYarn[index];
    availableYarn = availableYarn.filter((e) => e != choice);
    participant.number = choice;
  }

  // event listeners
  joinButton.addEventListener("click", connect);
  startStreamButton.addEventListener("click", startStream);
  stopStreamButton.addEventListener("click", stopStream);
});
