from flask import Blueprint, request, jsonify, abort
from datetime import datetime
from app.services.stashpoint_search import find_available_stashpoints

# Blueprint registered under /api/v1/stashpoint_search, not /api/v1/stashpoints
bp = Blueprint("stashpoint_search", __name__, url_prefix="/api/v1/stashpoint_search")

@bp.route("/", methods=["GET"])
def search_stashpoints():
    
    print("Just checking")

    # Parse & validate query parameters
    lat = float(request.args["lat"])
    lng = float(request.args["lng"])
    dropoff_str = request.args["dropoff"]
    pickup_str = request.args["pickup"]
    bag_count = int(request.args.get("bag_count", 1))
    radius_km = float(request.args.get("radius_km", 10))

    if bag_count <= 0:
        abort(400, "Bag count must be greater than 0")

    # Parse datetime strings
    dropoff = datetime.fromisoformat(dropoff_str)
    pickup = datetime.fromisoformat(pickup_str)

    if dropoff >= pickup:
        abort(400, "Dropoff time must be before pickup time")

    # Perform stashpoint search logic
    results = find_available_stashpoints(lat, lng, dropoff, pickup, bag_count, radius_km)
    return jsonify(results), 200
