# Model Card — Prediksi Kesesuaian Usaha Alumni

## Ringkasan

- Algoritma: Random Forest Classifier
- Preprocessing: OneHotEncoder untuk kategori dan passthrough untuk numerik
- Jumlah data: 1.500 baris sintetis
- Kelas: Sangat Sesuai, Sesuai, Kurang Sesuai, Tidak Sesuai
- Akurasi data uji: 86,67%
- Rata-rata 3-fold cross-validation: 85,20% ± 1,56%

## Fitur

- jurusan
- nilai_ujikom
- nilai_kejuruan
- tempat_pkl_relevan
- ekskul_aktif
- usaha_jenis
- tingkat_relevansi_usaha
- usaha_lama_berjalan
- pendapatan

## Fitur yang sengaja tidak dipakai

- `status_tracer`: nilainya konstan Wirausaha sehingga tidak membawa informasi.
- `usaha_lokasi`: teks lokasi bebas tidak mengukur relevansi bidang usaha.
- `skor_kesesuaian_usaha`: merupakan hasil/rubrik target dan tidak boleh masuk ke fitur training.

## Keterbatasan

- Dataset sintetis mempelajari rubrik yang dirancang, bukan realitas alumni secara langsung.
- Kelas Sesuai berdekatan dengan Sangat Sesuai dan Kurang Sesuai sehingga performanya lebih rendah.
- Daftar jenis usaha harus distandardisasi; input teks bebas dapat menimbulkan variasi yang tidak dikenali.
- Confidence model bukan probabilitas bahwa penilaian itu benar secara objektif.

## Penggunaan yang tepat

Model digunakan sebagai informasi pendukung bagi pengelola tracer study. Hasil tidak boleh diperlakukan sebagai keputusan mutlak atau sebagai pengganti penilaian pakar.
