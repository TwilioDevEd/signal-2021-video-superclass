# Code snippets

## CURL request for token

curl -X POST http://localhost:5000/token -H "Content-Type: application/json" -d '{"identity": "Sarah"}'

## Video Room Monitor

<script src="https://cdn.jsdelivr.net/npm/@twilio/video-room-monitor/dist/browser/twilio-video-room-monitor.js"></script>

      Twilio.VideoRoomMonitor.registerVideoRoom(room);
      Twilio.VideoRoomMonitor.openMonitor();

## Network Bandwidth Profile API

https://www.twilio.com/docs/video/tutorials/using-bandwidth-profile-api

## Simulcast docs

https://www.twilio.com/docs/video/tutorials/working-with-vp8-simulcast

## Diagnostic app URL

https://rtc-diagnostics-video-0pro029u-8723-dev.twil.io
