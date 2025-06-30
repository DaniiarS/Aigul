# from app.db.database import SessionLocal
# from app.db.models import BusStop

# db = SessionLocal()

# try:
#     bus_stops = db.query(BusStop).all()
#     MAX_SIZE = 6

#     for bs in bus_stops:
#         lon_q, lon_r = bs.lon.split(".")
#         lat_q, lat_r = bs.lat.split(".")

#         if len(lon_r) < MAX_SIZE:
#             delta = MAX_SIZE - len(lon_r)
#             lon_r = lon_r + "0" * delta 

#             print("Before:", bs.lon)
#             bs.lon = lon_q + "." + lon_r
#             print("Aftere:", bs.lon)
#             # db.commit()
#             print()
        
#         if len(lat_r) < MAX_SIZE:
#             delta1 = MAX_SIZE - len(lat_r)
#             lat_r = lat_r + "0" * delta1

#             print("Before:", bs.lat)
#             bs.lat = lat_q + "." + lat_r
#             print("Aftere:", bs.lat)
#             # db.commit()
#             print()

# except Exception as e:
#     print(f"Unexpected error: {e}")
# finally:
#     db.close()