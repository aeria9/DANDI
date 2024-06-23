import streamlit as st
import folium
import json
import pandas as pd
from streamlit.components.v1 import html

# Set page configuration for a better appearance
st.set_page_config(
    page_title="Peta Kepadatan Penduduk",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

colors = [
    "#67000d",  # Merah sangat gelap
    "#a50f15",
    "#cb181d",
    "#ef3b2c",
    "#fb6a4a",
    "#fc9272",
    "#fcbba1",
    "#fee0d2",
    "#fff5f0",
    "#f7e1de",  # Merah sangat terang
]


# Fungsi untuk memuat data CSV
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# Membaca data dari file CSV
data = load_data('data.csv')

# Menampilkan judul untuk peta di sidebar
st.sidebar.markdown("<h1 style='text-align: left; color: #008000;'>Peta Kepadatan Penduduk Banggae Timur</h1>", unsafe_allow_html=True)

st.sidebar.write("Kecamatan Banggae Timur merupakan salah satu kecamatan yang terletak di Kabupaten Majene, Provinsi Sulawesi Barat, Indonesia.")
st.sidebar.write("Setiap warna mewakili tingkat kepadatan yang berbeda, dengan warna hijau tua menunjukkan kepadatan tertinggi.")
# Menampilkan data dalam tabel di sidebar
st.sidebar.write("Data yang digunakan:")
st.sidebar.dataframe(data)

# Membaca data GeoJSON
with open('map.geojson') as f:
    geojson_data = json.load(f)

# Mengambil kepadatan penduduk dari atribut KEPADATAN di GeoJSON
densities = [feature['properties']['KEPADATAN'] for feature in geojson_data['features']]
min_density = min(densities)
max_density = max(densities)

# Fungsi untuk membuat popup untuk setiap fitur pada peta Folium
def popup_function(feature):
    density = feature['properties']['KEPADATAN']
    return folium.Popup(f"Nama Desa: {feature['properties']['DESA']}<br>KEPADATAN: {density}", parse_html=True)

# Mengurutkan fitur GeoJSON berdasarkan kepadatan dari tinggi ke rendah
sorted_features = sorted(geojson_data['features'], key=lambda x: x['properties']['KEPADATAN'], reverse=True)

# Membuat daftar warna sesuai dengan urutan fitur yang diurutkan
feature_colors = {feature['properties']['DESA']: colors[i % len(colors)] for i, feature in enumerate(sorted_features)}

# Membuat objek peta Folium
m = folium.Map(location=[-3.5403, 118.9727], zoom_start=12)

# Menambahkan data GeoJSON ke peta dengan warna sesuai urutan kepadatan dan popup
for feature in sorted_features:
    desa_name = feature['properties']['DESA']
    color = feature_colors.get(desa_name, '#cccccc')  # Default color jika tidak ada warna yang cocok
    
    style_function = lambda x, color=color: {
        'fillColor': color,
        'color': 'grey',
        'weight': 1,
        'fillOpacity': 0.7,
    }
    
    geojson_layer = folium.GeoJson(
        feature,
        style_function=style_function,
        popup=popup_function(feature)
    )
    geojson_layer.add_to(m)

# Menyesuaikan peta agar memuat semua data GeoJSON
m.fit_bounds(m.get_bounds())

# Menyimpan peta ke file HTML sementara
m.save('index.html')

# Membaca konten HTML dari file
with open('index.html', 'r', encoding='utf-8') as f:
    map_html = f.read()


# Menampilkan peta di Streamlit menggunakan komponen HTML
html(map_html, height=600)
