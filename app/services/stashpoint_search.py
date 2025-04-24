from sqlalchemy import func, literal
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from geoalchemy2.types import Geography
from app import db
from app.models.stashpoint import Stashpoint
from app.models.booking import Booking

def find_available_stashpoints(lat: float, lng: float,
                               dropoff: datetime, pickup: datetime,
                               bag_count: int, radius_km: float = 10.0):
    # 1) Input validation
    if bag_count <= 0:
        raise ValueError("bag_count must be > 0")
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise ValueError("Latitude or longitude out of bounds")
    if dropoff >= pickup:
        raise ValueError("dropoff must be before pickup")

    # 2) Build search geography point once
    geom = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
    geog = func.cast(geom, Geography())  # only needed if column isn’t geography

    radius_m = radius_km * 1000

    # 3) Overlapping‐bookings subquery
    overlapping = (
        db.session.query(
            Booking.stashpoint_id.label("sid"),
            func.coalesce(func.sum(Booking.bag_count), 0).label("total_bags")
        )
        .filter(
            Booking.is_cancelled.is_(False),
            Booking.dropoff_time < pickup,
            Booking.pickup_time  > dropoff
        )
        .group_by(Booking.stashpoint_id)
        .subquery()
    )

    # 4) Compute available capacity
    avail = Stashpoint.capacity - func.coalesce(overlapping.c.total_bags, 0)

    # 5) Distance as km (relies on geography on both sides)
    dist_km = func.ST_Distance(geog, Stashpoint.location) / 1000.0

    # 6) Main query
    q = (
        db.session.query(
            Stashpoint,
            dist_km.label("distance_km"),
            avail.label("available_capacity"),
        )
        .outerjoin(overlapping, Stashpoint.id == overlapping.c.sid)
        .filter(func.ST_DWithin(geog, Stashpoint.location, literal(radius_m)))
        .filter(avail >= bag_count)
        .filter(
            Stashpoint.open_from <= dropoff.time(),
            Stashpoint.open_until >= pickup.time()
        )
        .order_by(dist_km)
    )

    try:
        # print("[DEBUG SQL]", q.statement.compile(compile_kwargs={"literal_binds": True}))
        results = q.all()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise

    # 7) Format
    return [
        { **sp.to_dict(),
          "distance_km": round(d, 2),
          "available_capacity": int(c)
        }
        for sp, d, c in results
    ]
