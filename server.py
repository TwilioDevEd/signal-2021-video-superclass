import json
import os

import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest
from dotenv import load_dotenv
from flask import Flask, render_template, request
from twilio.rest.media.v1 import media_processor

# Create a Flask app
app = Flask(__name__)

# Load environment variables from a `.env` file
load_dotenv()

# Twilio client initialization
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY"]
api_secret = os.environ["TWILIO_API_SECRET"]

# Room settings
ROOM_NAME = "Superclass!"
MAX_PARTICIPANTS = 6

twilio_client = twilio.rest.Client(api_key, api_secret, account_sid)


def find_or_create_room():
    """Find an existing Video Room, or create one if it doesn't exist."""
    try:
        # Try to fetch an in-progress Video room with the name that's the value of the global
        # ROOM_NAME variable
        room = twilio_client.video.rooms(ROOM_NAME).fetch()
    except twilio.base.exceptions.TwilioRestException:
        # If an in-progress room with the name we tried to fetch doesn't exist, create one
        room = twilio_client.video.rooms.create(
            unique_name=ROOM_NAME,
            # constrain the number of allowed participants
            max_participants=MAX_PARTICIPANTS,
            # use a group room (as opposed to `go` for WebRTC Go, or `p2p` for Peer rooms)
            type="group",
        )
    # Print how many participants the room has
    print(f"{room.unique_name} has {len(room.participants.list())} participants in it.")


def fetch_player_streamer():
    """Check if there is already a PlayerStreamer created.

    This application assumes that there will only ever be one running
    PlayerStreamer at a time, thus only ever one livestream going at a time.
    """
    player_streamers = twilio_client.media.player_streamer.list(status="started")
    if len(player_streamers) == 0:
        return
    return player_streamers[0]


def create_livestream():
    """Create a PlayerStreamer and MediaProcessor.

    The MediaProcessor will run a Video Composer that joins the
    specified video room, captures it audio/video data, formats
    it in a livestream, and sends it to the PlayerStreamer listed
    in the `outputs`.

    See Video Composer docs for more information about what to pass
    into the extension_context: https://www.twilio.com/docs/live/video-composer
    """
    # Create the PlayerStreamer
    player_streamer = twilio_client.media.player_streamer.create()
    # Create the MediaProcessor. Once the MediaProcessor is created,
    # the Video Composer will join the room and start sending
    # livestream content to the PlayerStreamer. The PlayerStreamer
    # then makes that livestream available to your frontend
    # via a Player SDK.
    media_processor = twilio_client.media.media_processor.create(
        extension="video-composer-v1",
        extension_context=json.dumps(
            {
                "room": {
                    # This can be the room SID or unique name
                    "name": ROOM_NAME
                },
                # optional, this can be whatever name you want the Video Composer to use
                # when it joins the video room.
                "identity": "livestreamer",
                "outputs": [player_streamer.sid],
            }
        ),
    )
    print(
        f"Created livestream with MediaProcessor {media_processor.sid} and PlayerStreamer {player_streamer.sid}"
    )


def stop_livestream():
    """Stop all active resources when the livestream is finished.

    It's important to clean up all resources when done. See Billing and
    Resource Management documentation for more information:
    https://www.twilio.com/docs/live/billing-and-resource-management
    """
    # Retrieve all active resources: PlayerStreamers in the `created` or `started` state,
    # or MediaProcessors in the `started` state
    created_player_streamers = twilio_client.media.player_streamer.list(
        status="created"
    )
    started_player_streamers = twilio_client.media.player_streamer.list(
        status="started"
    )
    started_media_processors = twilio_client.media.media_processor.list(
        status="started"
    )
    # End any active resources
    for resources in [
        created_player_streamers,
        started_player_streamers,
        started_media_processors,
    ]:
        for resource in resources:
            resource.update(status="ended")
    print("Stopped all resources.")


@app.route("/")
def serve():
    """Render the homepage.

    This is the landing page where speakers in the livestream will join.

    This page will also show a message when someone signs on about whether or not they
    have any livestream currently going on.
    """
    find_or_create_room()
    player_streamer = fetch_player_streamer()
    streaming_status = (
        "You are not streaming" if not player_streamer else "You are streaming"
    )
    return render_template("index.html", streaming_status=streaming_status)


@app.route("/stream")
def serve_livestream():
    """Render the page where an audience can stream content."""

    return render_template("stream.html")


@app.route("/token", methods=["POST"])
def get_token():
    """Create and return an Access Token for a specific participant to join the video room"""
    # retrieve the participant's identity from the request's JSON payload
    identity = request.json.get("identity")
    # create an access token with your account credentials and the participant's identity
    access_token = twilio.jwt.access_token.AccessToken(
        account_sid, api_key, api_secret, identity=identity
    )
    # create a video grant that will allow access to this app's specific video room
    video_grant = twilio.jwt.access_token.grants.VideoGrant(room=ROOM_NAME)
    # Add the video grant to the access token
    access_token.add_grant(video_grant)
    # Turn the access token into a string and send it back as the response
    return {"token": access_token.to_jwt()}


@app.route("/stream-token", methods=["POST"])
def get_streaming_token():
    """Create and return an Access Token for an audience member to watch a stream.

    The difference between this endpoint and the `/token` endpoint above is that
    this one generates an Access Token with a PlaybackGrant, which can be used to
    view a livestream, and the one above generates a VideoGrant, which can be used
    to enter a Video Room."""
    player_streamer = fetch_player_streamer()
    # if there is no PlayerStreamer, no livestream is in process.
    if not player_streamer:
        return {"token": None, "message": "The stream is not in progress"}
    access_token = twilio.jwt.access_token.AccessToken(account_sid, api_key, api_secret)
    # Retrieve a PlaybackGrant from the Twilio API
    playback_grant = player_streamer.playback_grant().create()
    # Attach that PlaybackGrant to the Access Token.
    access_token.add_grant(
        twilio.jwt.access_token.grants.PlaybackGrant(playback_grant.grant)
    )
    return {"token": access_token.to_jwt(), "message": "success"}


@app.route("/start-stream")
def start_livestream():
    player_streamer = fetch_player_streamer()
    if player_streamer:
        # The stream has already started, so just return an empty response
        return {"message": "success"}
    # Create the livestream
    create_livestream()
    return {"message": "success"}


@app.route("/stop-stream")
def stop_stream():
    """End all livestreaming resources."""
    stop_livestream()
    return {"message": "success"}


# Start the server when we run this file
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
