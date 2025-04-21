
import streamlit as st
import openrouteservice
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# --- Setup ---
st.set_page_config(page_title="Nearest Green Building", layout="wide")
st.title("📍 Nearest Green Building by Road & Air")

# --- OpenRouteService Client ---
API_KEY = '5b3ce3597851110001cf6248f80d6ed534184a8481b000c5b82f4566'
client = openrouteservice.Client(key=API_KEY)

# --- Sidebar: User input for movable location ---
st.sidebar.header("📍 Enter Your Location")
lat = st.sidebar.number_input("Latitude", value=12.9716, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.5640, format="%.6f")

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
    ("Place B", (12.9725, 77.5910)),
    ("Place C", (12.9760, 77.5900)),
    ("Place D", (12.9740, 77.5955)),
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
    nearest = min(distances, key=lambda x: x[3])
    nearestAir = min(distances, key=lambda x: x[2])

    st.success(f"✅ Nearest by road: **{nearest[0]}** ({nearest[3]:.2f} km) \n ✅ Nearest by AIR: **{nearestAir[0]}** ({nearestAir[2]:.2f} m)")
    
else:
    st.error("❌ No valid routes found.")
    st.stop()

# --- Show table of distances ---
st.subheader("📏 Distance Summary")
for name, coord, geo_m, road_km in distances:
    st.markdown(f"**{name}** — Road: `{road_km:.2f} km`, Geo: `{geo_m:.0f} m` Factor: `{road_km/(geo_m/1000)}`")

# --- Create Folium Map ---
m = folium.Map(location=movable_point, zoom_start=15)

# Add movable marker
folium.Marker(
    location=movable_point,
    popup="📍 You (Snapped)",
    icon=folium.Icon(color='red')
).add_to(m)

# Draw circles of 100m, 300m, 500m
for radius, color in [(1000, "cyan"), (2000, "purple"), (3000, "orange"), (4000, "indigo"), (5000, "yellow")]:
    folium.Circle(
        location=movable_point,
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.1,
        popup=f"{radius}m radius"
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
