import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from geopy.geocoders import Nominatim
import matplotlib.image as mpimg
import os

# Buat dictionary agar bisa dipilih berdasarkan nama kota
city_names = ['Aotizhongxin', 'Changping', 'Dingling', 'Dongsi', 'Guanyuan',
              'Gucheng', 'Huairou', 'Nongzhanguan', 'Shunyi', 'Tiantan',
              'Wanliu', 'Wanshouxigong']

all_data = pd.read_csv('.\dashboard\dashboard.csv')
# all_data = os.path.join(os.path.dirname(__file__), "dashboard.csv")

# Membuat Dashboard
st.header('Dashboard Data Kualitas Udara di Negara China')

# Sidebar untuk memilih kota
with st.sidebar:
    st.header('Data Kualitas Udara di Kota Cina')
    selected_city = st.radio("Pilih Kota yang ingin Anda lihat", city_names, horizontal=False)

# Convert date column to datetime
all_data['date'] = pd.to_datetime(all_data['date'])

# Ambil data berdasarkan kota yang dipilih
df_selected = all_data[all_data['station'] == selected_city]

# # Resampling data untuk mendapatkan rata-rata bulanan PM10
data_time_series = df_selected[['date', 'PM10']].set_index('date').resample('ME').mean()

# Plot nilai PM10
fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(data_time_series.index, data_time_series['PM10'], label=f"PM10 - {selected_city}", color='b')
ax.set_title(f"PM10 di {selected_city} (Rata-rata Bulanan)")
ax.legend()
ax.grid()

# # Tampilkan plot di Streamlit
st.pyplot(fig)

#hitung nilai max dari kota yang dipilih
max_PM10 = df_selected["PM10"].max()
max_date = df_selected[df_selected["PM10"] == max_PM10].date.values[0]
max_date = pd.to_datetime(max_date)

# Menampilkan kota yang dipilih
st.caption(f"Nilai PM10 tertinggi pada kota **{selected_city}** memiliki nilai sebesar **{max_PM10}**")
st.caption(f"terjadi pada tanggal: **{max_date}**")

# memberikan keterangan
with st.expander("Explanation"):
    st.write(
        """
        Pada kota yang Anda pilih, kami menampilkan rata-rata bulanan nilai PM10.
        PM10 adalah partikel kecil yang dapat masuk ke paru-paru dan menyebabkan masalah kesehatan.
        apabila menghirup udara dengan nilai PM10 yang tinggi dapat menyebabkan masalah pada paru-paru.
        """
    )
                                           
# Menghitung rata-rata PM10 untuk semua kota per bulan
data_all_time_series = all_data[['date', 'PM10']].set_index('date').resample('ME').mean()

# Mencari nilai maksimum PM10 dan tanggalnya
max_pm10_value = data_all_time_series['PM10'].max()
max_pm10_date = data_all_time_series['PM10'].idxmax()

# Loop untuk menyimpan data TEMP dan PM10 dari tahun 2015–2017
all_data['date'] = pd.to_datetime(all_data['date'])  # Pastikan kolom 'date' dalam format datetime
date_data = all_data['date']

# Resample TEMP
temp_resampled = all_data[['date', 'TEMP']].set_index('date').resample('ME').mean()
temp_time_series = temp_resampled.loc['2015':'2017']

# Resample PM10
pm10_resampled = all_data[['date', 'PM10']].set_index('date').resample('ME').mean()
pm10_time_series = pm10_resampled.loc['2015':'2017']

# Gabungkan semua TEMP dan PM10 berdasarkan tanggal
temp_time_series.columns = list(temp_time_series.keys())
avg_temp = temp_time_series.mean(axis=1)

pm10_time_series.columns = list(pm10_time_series.keys())
avg_pm10 = pm10_time_series.mean(axis=1)

temp_pm10, ax = plt.subplots(figsize=(15, 6))
ax.plot(avg_temp.index, avg_temp, label='Rata-rata TEMP', color='orange')
ax.plot(avg_pm10.index, avg_pm10, label='Rata-rata PM10', color='green')
ax.set_title('Rata-rata Bulanan TEMP dan PM10 Semua Kota (2015 - 2017)')
ax.legend()
ax.grid()

numeric_data = all_data[['TEMP', 'PM10']]
corelation_matrix = numeric_data.corr()
corr_plt, ax = plt.subplots(figsize=(15, 6))
sns.heatmap(corelation_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
ax.set_title("Matriks Korelasi Semua Kota")

def plot_china_map(data):
    # Path ke file gambar lokal
    image_path = './china.jpg'

    # Membaca gambar peta China dari file lokal
    china_map = mpimg.imread(image_path)

    # Membuat plot
    map_pt,ax = plt.subplots(figsize=(10,10))
    # Disesuaikan dengan batas geografis China
    plt.imshow(china_map, extent=[73, 135, 18, 53], alpha=0.6) 
    ax.scatter(data['longitude'], data['latitude'], s=5, c='red', label='stasiun pemantauan')
    ax.set_title("Lokasi Stasiun Pemantauan Kualitas Udara di China")
    ax.legend()
    # Menampilkan plot
    st.pyplot(map_pt)

# Membersihkan data (hapus baris dengan NaN)
all_data = all_data.dropna(subset=['longitude', 'latitude'])

# Plot nilai PM10 di setiap kota
tot_PM, ax = plt.subplots(figsize=(15, 6))
ax.plot(data_all_time_series.index, data_all_time_series['PM10'], linestyle = '-', label='PM10', color = 'b')
# Menandai titik maksimum dengan warna merah
ax.scatter(max_pm10_date, max_pm10_value, color='red', s=300, marker='*', label=f'Max PM10')
ax.set_title(f"Rata-rata Nilai PM10 per Bulan di Semua Kota")
ax.legend()
ax.grid()

tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    st.header("Rata-rata nilai PM10 Setiap Bulan")
    # Tampilkan plot di Streamlit
    st.pyplot(tot_PM)
    with st.expander("See explanation"):
        st.write(
            """
            informasi diatas adalah grafik dari rata-rata nilai PM10 setiap bulan 
            pada dua belas kota yang ada di China.Grafik ini menunjukkan bahwa 
            nilai PM10 pada bulan-bulan tertentu lebih tinggi dibandingkan bulan lainnya.
            """
        )

with tab2:
    st.header("Korelasi Nilai PM10 dan TEMP")
    # Tampilkan plot di Streamlit
    st.pyplot(temp_pm10)
    st.pyplot(corr_plt)
    with st.expander("See explanation"):
        st.write(
            """
            Korelasi adalah hubungan antara dua variabel.
            Gambar diatas menunjukkan hubungan antara nilai PM10 dan TEMP.
            bisa dilihat nilai PM10 memiliki korelasi kecil dengan nilai TEMP
            jika nilai PM10 tinggi maka TEMP tidak terpengaruh
            """
        )

with tab3:
    st.header("Peta Stasiun Pemantauan Kualitas Udara")
    # Menampilkan peta
    plot_china_map(all_data)
    with st.expander("See explanation"):
        st.write(
            """
            peta diatas adalah peta negara China yang menunjukkan lokasi stasiun pemantauan kualitas udara.
            peta ini menunjukkan bahwa stasiun pemantauan tersebar di seluruh wilayah China.
            namun tidak semua wilayah memiliki stasiun pemantauan. hanya bagian tengah
            yang memiliki stasiun pemantauan saja.
            """
        )