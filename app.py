# import streamlit as st
# import openrouteservice
# from geopy.distance import geodesic
# import folium
# from streamlit_folium import st_folium

# # --- API Setup ---
# API_KEY = '5b3ce3597851110001cf6248f80d6ed534184a8481b000c5b82f4566'
# client = openrouteservice.Client(key=API_KEY)

# st.set_page_config(page_title="Nearest Place Finder", layout="wide")
# st.title("📍 Nearest Place by Road & Air (Folium + OpenRouteService)")

# # --- Sidebar for movable point ---
# st.sidebar.header("Enter Your Location")
# lat = st.sidebar.number_input("Latitude", value=12.9716, format="%.6f")
# lon = st.sidebar.number_input("Longitude", value=77.5640, format="%.6f")
# movable_point = (lat, lon)  # this is (lat, lon)

# # --- Fixed Places (name, (lat, lon)) ---
# fixed_places = [
#     ("Place A", (12.9716, 77.5946)),
#     ("Place B", (12.9716, 77.5949)),
#     ("Place C", (12.9716, 77.4444)),
#     ("Place D", (12.48, 77.40)),
#     ("Place E", (12.40, 77.40)),
#     ("Place F", (12.00, 77.00))
# ]

# # --- Compute distances ---
# distances = []
# for name, coord in fixed_places:
#     try:
#         route = client.directions(
#             coordinates=[(movable_point[1], movable_point[0]), (coord[1], coord[0])],  # (lon, lat)
#             profile='driving-car',
#             format='geojson'
#         )
#         road_km = route['features'][0]['properties']['summary']['distance'] / 1000
#         geo_m = geodesic(movable_point, coord).meters
#         distances.append((name, coord, geo_m, road_km))
#     except Exception as e:
#         st.error(f"Error calculating distance to {name}: {e}")

# # --- Nearest Place ---
# nearest = min(distances, key=lambda x: x[2])  # by arial

# # --- Show distance summary ---
# st.subheader("📏 Distance Table")
# for name, coord, geo_m, road_km in distances:
#     st.write(f"**{name}** - Road: {road_km:.2f} km | Geodesic: {geo_m:.0f} m | Factor: {road_km/(geo_m/1000)}")

# st.success(f"✅ Nearest by geo: **{nearest[0]}** ({nearest[2]:.2f} m)")

# # --- Render Folium Map ---
# m = folium.Map(location=movable_point, zoom_start=13)

# # Movable marker (your location)
# folium.Marker(
#     location=movable_point,
#     popup="📍 You",
#     icon=folium.Icon(color='red')
# ).add_to(m)

# # Fixed markers
# for name, coord, geo_m, road_km in distances:
#     folium.Marker(
#         location=coord,
#         popup=f"{name}<br>Road: {road_km:.2f} km<br>Geo: {geo_m:.0f} m<br>Factor: {road_km/(geo_m/1000)}",
#         icon=folium.Icon(color='green')
#     ).add_to(m)

# # Line to nearest
# folium.PolyLine([movable_point, nearest[1]], color='blue', weight=4).add_to(m)

# # --- Display map in Streamlit ---
# st.subheader("🗺️ Map View")
# st_folium(m, width=900, height=600)

import streamlit as st
import openrouteservice
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# --- Setup ---
st.set_page_config(page_title="Nearest Place Finder", layout="wide")
st.title("📍 Nearest Place by Road & Air (Folium + OpenRouteService)")

# --- OpenRouteService Client ---
API_KEY = '5b3ce3597851110001cf6248f80d6ed534184a8481b000c5b82f4566'
client = openrouteservice.Client(key=API_KEY)

# --- Sidebar: User input for movable location ---
st.sidebar.header("📍 Enter Your Location")
lat = st.sidebar.number_input("Latitude", value=12.50, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.50, format="%.6f")

# --- Function: Snap to road using reverse geocode ---
def snap_to_road(lat, lon):
    try:
        result = client.pelias_reverse((lon, lat))
        snapped = result['features'][0]['geometry']['coordinates']
        return (snapped[1], snapped[0])  # return as (lat, lon)
    except Exception as e:
        st.warning(f"⚠️ Could not snap to road. Using entered coordinates.\nError: {e}")
        return (lat, lon)

# --- Snap user's location ---
movable_point = snap_to_road(lat, lon)

# --- Fixed locations: name + (lat, lon) ---
fixed_places = [
    ("Place A", (12.9716, 77.5946)),
    ("Place B", (12.9716, 77.5949)),
    ("Place C", (12.9716, 77.4444)),
    ("Place D", (12.48, 77.40)),
    ("Place E", (12.40, 77.40)),
    ("Place F", (12.00, 77.00))
]

# --- Calculate distances ---
distances = []
for name, coord in fixed_places:
    try:
        route = client.directions(
            coordinates=[(movable_point[1], movable_point[0]), (coord[1], coord[0])],
            profile='driving-car',
            format='geojson'
        )
        road_km = route['features'][0]['properties']['summary']['distance'] / 1000
        geo_m = geodesic(movable_point, coord).meters
        distances.append((name, coord, geo_m, road_km))
    except Exception as e:
        st.error(f"Error calculating distance to {name}: {e}")

# --- Find nearest by road ---
if distances:
    nearest = min(distances, key=lambda x: x[2])
    st.success(f"✅ Nearest by Air: **{nearest[0]}** ({nearest[2]:.2f} m)")
else:
    st.error("❌ No valid routes found.")
    st.stop()

# --- Show table of distances ---
st.subheader("📏 Distance Summary")
for name, coord, geo_m, road_km in distances:
    st.markdown(f"**{name}** — Road: `{road_km:.2f} km`, Geo: `{geo_m:.0f} m`, Factor: `{road_km/(geo_m/1000)}`")

# --- Create Folium Map ---
m = folium.Map(location=movable_point, zoom_start=15)

# Add user's marker
folium.Marker(
    location=movable_point,
    popup="📍 You (Snapped)",
    icon=folium.Icon(color='red')
).add_to(m)

# Add fixed markers
for name, coord, geo_m, road_km in distances:
    folium.Marker(
        location=coord,
        popup=f"{name}<br>Road: {road_km:.2f} km<br>Geo: {geo_m:.0f} m<br>Factor: {road_km/(geo_m/1000)}",
        icon=folium.Icon(color='green')
    ).add_to(m)

# Line to nearest place
folium.PolyLine([movable_point, nearest[1]], color='blue', weight=4).add_to(m)

# --- Show map ---
st.subheader("🗺️ Map View")
st_folium(m, width=900, height=600)
