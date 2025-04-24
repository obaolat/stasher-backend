# app/routes/stashpoints.py

from flask import Blueprint, request, jsonify, abort
from datetime import datetime
from app.services.stashpoint_search import find_available_stashpoints
from app.models.stashpoint import Stashpoint

bp = Blueprint("stashpoints", __name__, url_prefix="/api/v1/stashpoints")

# exactly these keys, no more no less, triggers a search
SEARCH_KEYS = {"lat", "lng", "dropoff", "pickup", "bag_count", "radius_km"}

@bp.route("/", methods=["GET"])
def list_or_search_stashpoints():
    args = request.args

    # 1) No params => list ALL
    if not args:
        all_sp = Stashpoint.query.all()
        return jsonify([sp.to_dict() for sp in all_sp]), 200

    # 2) If the set of provided keys != SEARCH_KEYS => 404
    provided = set(args.keys())
    if provided != SEARCH_KEYS:
        abort(404, f"Expected exactly parameters {sorted(SEARCH_KEYS)}, got {sorted(provided)}")

    # 3) Parse & validate formats (400 on any ValueError)
    try:
        lat       = float(args["lat"])
        lng       = float(args["lng"])
        dropoff   = datetime.fromisoformat(args["dropoff"])
        pickup    = datetime.fromisoformat(args["pickup"])
        bag_count = int(args["bag_count"])
        radius_km = float(args["radius_km"])

        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("lat/lng out of bounds")
        if dropoff >= pickup:
            abort(400, "dropoff must be before pickup")
        if bag_count < 1:
            abort(400, "bag_count must be ≥ 1")

    except ValueError as ve:
        abort(400, f"Bad parameter format: {ve}")

    # 4) All good → run the search
    results = find_available_stashpoints(
        lat, lng, dropoff, pickup, bag_count, radius_km
    )
    return jsonify(results), 200
