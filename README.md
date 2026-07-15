# Modul Prediksi Kesesuaian Usaha Alumni

Paket ini menambahkan prediksi empat kelas untuk alumni berstatus **Wirausaha**:

- Sangat Sesuai
- Sesuai
- Kurang Sesuai
- Tidak Sesuai

## Prinsip penilaian

Kesesuaian usaha berarti hubungan antara **jenis usaha** dan **kompetensi jurusan**. Pendapatan dan lama usaha hanya menjadi indikator pendukung keberlanjutan. Karena itu, keduanya tidak boleh dijadikan bukti utama bahwa usaha sesuai dengan jurusan.

## Isi paket

- `dataset_wirausaha_1500_multiclass.csv`: dataset sintetis 1.500 baris.
- `train_model_wirausaha.ipynb`: notebook training dan evaluasi.
- `model_wirausaha_pipeline.pkl`: model dan preprocessing dalam satu pipeline.
- `app_wirausaha.py`: API FastAPI untuk Railway.
- `requirements.txt` dan `Procfile`: kebutuhan deployment.
- `sql_migrasi_wirausaha.sql`: penambahan kolom hasil prediksi.
- `prediksi_kesesuaian_wirausaha.php`: halaman prediksi alumni.
- `prediksi_kesesuaian_wirausaha_admin.php`: batch prediksi untuk admin.
- `analisis_wirausaha.php`: tabel analisis admin.
- `laporan_grafik_wirausaha.php`: visualisasi hasil.
- `usaha_jenis_options.php`: opsi dropdown jenis usaha terstandar.

## Catatan akademik penting

Dataset ini **sintetis berbasis rubrik**, bukan data hasil observasi alumni. Akurasi uji sekitar 86,7% hanya menunjukkan kemampuan model mempelajari pola dataset tersebut. Untuk skripsi final, label idealnya ditinjau oleh guru produktif/BKK atau pakar program keahlian dan model divalidasi kembali menggunakan data alumni nyata.

## Deployment API

1. Unggah seluruh file API, model, `requirements.txt`, dan `Procfile` ke repository Railway.
2. Atur environment variable `TRACER_API_TOKEN`.
3. Setelah aktif, salin URL Railway ke konfigurasi PHP pada dua file prediksi.
4. Endpoint yang digunakan: `POST /predict-wirausaha`.

## Perbedaan skor dan confidence

- `skor_kesesuaian_usaha`: estimasi tingkat kesesuaian 0–100.
- `confidence_usaha`: keyakinan model terhadap kelas yang dipilih, juga 0–100.

Jangan menampilkan confidence sebagai “persentase kesesuaian”, karena keduanya memiliki makna yang berbeda.
