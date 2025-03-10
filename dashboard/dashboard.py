import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from geopy.geocoders import Nominatim
import matplotlib.image as mpimg

# Dataset
data_dir = './data/'
data_files = ['PRSA_Data_Aotizhongxin_20130301-20170228.csv',
              'PRSA_Data_Changping_20130301-20170228.csv',
              'PRSA_Data_Dingling_20130301-20170228.csv',
              'PRSA_Data_Dongsi_20130301-20170228.csv',
              'PRSA_Data_Guanyuan_20130301-20170228.csv',
              'PRSA_Data_Gucheng_20130301-20170228.csv',
              'PRSA_Data_Huairou_20130301-20170228.csv',
              'PRSA_Data_Nongzhanguan_20130301-20170228.csv',
              'PRSA_Data_Shunyi_20130301-20170228.csv',
              'PRSA_Data_Tiantan_20130301-20170228.csv',
              'PRSA_Data_Wanliu_20130301-20170228.csv',
              'PRSA_Data_Wanshouxigong_20130301-20170228.csv']

# Buat dictionary agar bisa dipilih berdasarkan nama kota
city_names = ['Aotizhongxin', 'Changping', 'Dingling', 'Dongsi', 'Guanyuan',
              'Gucheng', 'Huairou', 'Nongzhanguan', 'Shunyi', 'Tiantan',
              'Wanliu', 'Wanshouxigong']
all_data = pd.read_csv('dashboard/dashboard.csv')

# Membaca dataset ke dictionary
data_kota = {city: pd.read_csv(data_dir + file) for city, file in zip(city_names, data_files)}

# Memperbaiki data
for city in data_kota:
    df = data_kota[city]
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df.fillna(df.mean(numeric_only=True), inplace=True)  # Mengisi NaN dengan rata-rata
    for column in df.select_dtypes(include=['object']).columns:
        mode_value = df[column].mode()[0]
        df.loc[:, column] = df[column].fillna(mode_value)  # Perbaikan

# Membuat Dashboard
st.header('Dashboard Data Kualitas Air di China')

# Sidebar untuk memilih kota
with st.sidebar:
    st.header('Data Kualitas Air di Kota Cina')
    selected_city = st.radio("Pilih Kota yang ingin Anda lihat", city_names, horizontal=False)

# Ambil data berdasarkan kota yang dipilih
df_selected = data_kota[selected_city]

# Resampling data untuk mendapatkan rata-rata bulanan PM10
data_time_series = df_selected[['date', 'PM10']].set_index('date').resample('ME').mean()

# Plot nilai PM10
fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(data_time_series.index, data_time_series['PM10'], label=f"PM10 - {selected_city}", color='b')
ax.set_title(f"PM10 di {selected_city} (Rata-rata Bulanan)")
ax.legend()
ax.grid()

# Tampilkan plot di Streamlit
st.pyplot(fig)

#hitung nilai max dari kota yang dipilih
max_PM10 = df_selected.PM10.max()
max_date = df_selected[df_selected.PM10 == max_PM10].date.values[0]
max_date = pd.to_datetime(max_date)

# Menampilkan kota yang dipilih
st.caption(f"Nilai PM10 tertinggi pada kota **{selected_city}** memiliki nilai sebesar **{max_PM10}**")
st.caption(f"terjadi pada tanggal: **{max_date}**")

with st.expander("Explanation"):
    st.write(
        """
        Pada kota yang Anda pilih, kami menampilkan rata-rata bulanan nilai PM10.
        PM10 adalah partikel kecil yang dapat masuk ke organ dalam manusia dan menyebabkan masalah kesehatan.
        apabila mengkonsumsi air dengan nilai PM10 yang tinggi dapat menyebabkan masalah pada pencernaan.
        """
    )

# ubah data menjadi datetime
all_data['date'] = pd.to_datetime(all_data['date'])
                                           
# Menghitung rata-rata PM10 untuk semua kota per bulan
data_all_time_series = all_data[['date', 'PM10']].set_index('date').resample('ME').mean()

# Mencari nilai maksimum PM10 dan tanggalnya
max_pm10_value = data_all_time_series['PM10'].max()
max_pm10_date = data_all_time_series['PM10'].idxmax()

# Memilih hanya kolom numerik
numeric_data = all_data.select_dtypes(include=['number'])

# Menghitung korelasi antar kolom numerik
correlation_matrix = numeric_data.corr()

def plot_china_map(data):
    # Path ke file gambar lokal
    image_path = 'china.jpg'

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
ax.set_title(f"PM10 Rata-rata Bulanan di Semua Kota")
ax.legend()
ax.grid()

# Plot nilai PM10 di setiap kota
corr_plt, ax = plt.subplots(figsize=(15, 6))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
ax.set_title("Korelasi antar Kolom Numerik")

tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    st.header("Rata-rata nilai PM10 Setiap Bulan")
    # Tampilkan plot di Streamlit
    st.pyplot(tot_PM)
    with st.expander("See explanation"):
        st.write(
            """
            informasi diatas adalah grafik dari rata-rata nilai PM10 setiap bulan pada dua belas kota yang ada di China.
            Grafik ini menunjukkan bahwa nilai PM10 pada bulan-bulan tertentu lebih
            tinggi dibandingkan bulan lainnya.
            """
        )

with tab2:
    st.header("Korelasi Pada Semua Nilai Numerik")
    # Tampilkan plot di Streamlit
    st.pyplot(corr_plt)
    with st.expander("See explanation"):
        st.write(
            """
            Korelasi adalah hubungan antara dua variabel.
            Nilai korelasi berkisar dari -1 hingga 1.
            Nilai 1 menunjukkan hubungan positif yang sempurna, 
            sedangkan -1 menunjukkan hubungan negatif yang sempurna.
            bisa dilihat nilai PM10 memiliki korelasi positif dengan nilai CO
            sehingga jika nilai PM10 tinggi maka nilai CO juga tinggi.
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
            namun tidak semua wilayah memiliki stasiun pemantauan. hanya bagian
            yang memiliki stasiun pemantauan saja yang terlihat pada peta.
            """
        )