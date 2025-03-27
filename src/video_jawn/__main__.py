import time
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
    redirect,
)
from video_jawn.coordinator import Coordinator, VideoFeedClient
from video_jawn.camera_utils.camera_feed import CameraFeed
from video_jawn.camera_utils.general import list_cameras
import argparse
import logging

app = Flask(__name__, template_folder="static")
coordinator = Coordinator()


@app.after_request
def add_header(response):
    # https://stackoverflow.com/questions/18251975/how-should-http-cache-actually-work
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/live")
def live():
    while coordinator.camera.height is None:
        time.sleep(0.1)
    width = int(coordinator.camera.width * 3 * coordinator.camera.video_scale)
    height = int(coordinator.camera.height * coordinator.camera.video_scale)
    return render_template("live.html", width=width, height=height)


@app.route("/start_system", methods=["POST"])
def start_system():
    if not coordinator.camera_active:
        coordinator.start_camera(
            int(request.form["videoSource"]), float(request.form["scale"])
        )
    return redirect("/live")


@app.route("/stop_system")
def stop_system():
    if coordinator.camera_active:
        coordinator.kill_camera()
    return redirect("/")


@app.route("/camera_list")
def camera_list():
    return jsonify({"available_cameras": list_cameras()})


@app.route("/status")
def status():
    return jsonify({"camera_active": coordinator.camera_active})


@app.route("/video_feed")
def video_feed():
    video_feed_client = VideoFeedClient()

    def video_frames():
        try:
            for frame in video_feed_client.get_frames():
                yield frame
        finally:
            video_feed_client.terminate()

    return Response(
        video_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/using_buffer_stream")
def using_buffer_stream():
    """
    Streams the 'using_buffer' value using Server-Sent Events (SSE).
    """

    def generate_events():
        last_value = None
        while True:
            current_value = coordinator.using_buffer
            # Only send an event if the value changed (optional optimization).
            if current_value != last_value:
                yield f"data: {current_value}\n\n"
                last_value = current_value
            time.sleep(0.05)  # Adjust how often you want to check/signal changes

    return Response(generate_events(), mimetype="text/event-stream")


@app.route("/change_color")
def change_color():
    val = int(request.args.get("color", "0"))
    if val not in [0, 1, 2]:
        return jsonify({"error": "color value out of range"}), 400
    coordinator.curr_color = val
    return ""


@app.route("/change_grayscale_intensity")
def change_grayscale_intensity():
    val = float(request.args.get("intensity", "1"))
    if not val >= 0 and val <= 2:
        return jsonify({"error": "intensity value out of range"}), 400
    coordinator.grayscale_intensity = val
    return ""


def serve(port, debug_level):
    logging.basicConfig(level=debug_level.upper())
    app.run(port=port)


def main():
    parser = argparse.ArgumentParser(
        prog="mypackage", description="Command-line interface for mypackage"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_serve = subparsers.add_parser("serve", help="Serve the Flask app")
    parser_serve.add_argument(
        "-p",
        "--port",
        type=int,
        default=10578,
        help="Port to run the server on (default: 10578)",
    )
    parser_serve.add_argument(
        "-d",
        "--debug",
        type=str,
        default="WARNING",
        help="Logging level (default: WARNING)",
    )

    args = parser.parse_args()

    if args.command == "serve":
        serve(args.port, args.debug)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
