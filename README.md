# Twilio Video Demo

## Livestreaming branch

This is the code based off that includes a Twilio Live video streaming
component.

## Running the application

You'll need Python3 to get this running. To install the required
dependencies:

```
python3 -m venv venv  # create a virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

Next, create a `.env` file. You'll put your account
credentials in that file, so that the Flask server can
connect to Twilio.

```
touch .env
```

In the .env file, you'll want these credentials:

```
TWILIO_ACCOUNT_SID=<your account SID>
TWILIO_API_KEY=<your api key>
TWILIO_API_SECRET=<your api key secret>
```

You can find your account SID in the [Twilio Console Dashboard](https://www.twilio.com/console).

You can create a new API key and get the secret through the
[Twilio Console](https://www.twilio.com/console/project/api-keys).

To run the Flask server:

```
source venv/bin/activate
python server.py
```

This will start a server that you can access on your
local machine at port 5000 (`localhost:5000`). You can view the application
at [http://localhost:5000](http://localhost:5000).

Can't wait to see what you build with Twilio Video!

## Access the Livestream

When you go to `http://localhost:5000`, you will see at the top of the page whether or not you are streaming.
You can start or stop the livestream for the Video Room (even if no one is in it; the Video Composer will still join
the room if you start streaming without anyone else in the room). You can also join the video room and invite others
to join.

To view the stream, you can navigate to [http://localhost:5000/stream](http://localhost:5000/stream). There you will
see a "Start Stream" button, which you can click to connect as an audience member to a stream,
if there is one in progress.

## Stop your stream when you are done

It is **very important** that you stop the livestream when you are finished, by pressing "Stop streaming this room." You might
also want to verify that you have no active livestreaming resources running when you are finished. If you do not stop the
livestream when you are finished, the resources will still continue running, and you will be billed for usage. To avoid
unnecessary usage charges, stop the stream when finished with it.

See [Billing and Resource Management](https://www.twilio.com/docs/live/billing-and-resource-management) for more information.
