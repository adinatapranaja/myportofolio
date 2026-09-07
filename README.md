# My Portofolio

Website portofolio pribadi milik **Adinata Alaudin Pranaja** untuk mata kuliah Pemrograman Berbasis Platform (PBP), kelas C.

- NPM: 2506656356
- Program studi: S1 Sistem Informasi, Universitas Indonesia

## Menjalankan proyek secara lokal

Prasyarat: Python 3 dan Git sudah terpasang.

```bash
# Buat dan aktifkan virtual environment (macOS/Linux)
python3 -m venv env
source env/bin/activate

# Instal dependency
pip install -r requirements.txt

# Siapkan database SQLite lokal dan jalankan server
python manage.py migrate
python manage.py runserver
```

Buka <http://localhost:8000> di browser. Untuk berhenti, tekan `Control+C`/`Ctrl+C`, lalu jalankan `deactivate` bila ingin keluar dari virtual environment.

Di Windows, aktivasi environment menggunakan:

```powershell
env\Scripts\activate
```

Sebelum menjalankan aplikasi secara lokal, pastikan berkas `.env` di root proyek berisi:

```env
PRODUCTION=False
```

## Konfigurasi production

Deployment PWS menggunakan PostgreSQL dan environment variables dari `.env.prod`. Isi kredensial database hanya melalui **PWS Project Credentials** dan simpan variabel tersebut pada tab **Environs** di dashboard PWS. Jangan commit `.env` atau `.env.prod` karena keduanya sudah dilindungi oleh `.gitignore`.

## Ringkasan Tutorial PBP

### Tutorial 0 — Setup Git Repository dan Django

Tutorial 0 menyiapkan fondasi proyek: membuat serta menghubungkan repository Git/GitHub, memahami branch dan pull request, membuat virtual environment, memasang dependency dari `requirements.txt`, lalu menginisialisasi proyek Django. Tutorial ini juga mengenalkan `.env` untuk mode lokal (SQLite) dan `.env.prod` untuk mode production (PostgreSQL/PWS).

Sumber: [Tutorial 0 PBP](https://pbp.cs.ui.ac.id/tutorial/tutorial-0.html).

### Tutorial 1 — Django Initial Project, HTML5, dan CSS3

Tutorial 1 melanjutkan proyek dengan mengganti package konfigurasi menjadi `portofolio`, membuat view dan routing untuk halaman utama, serta menghubungkan template dan static files. Halaman portofolio dibangun memakai elemen HTML semantik, CSS custom properties, Flexbox, CSS Grid, dan media query agar responsif. Tutorial ini juga memperkenalkan deployment ke PWS memakai WhiteNoise untuk static files.

Sumber: [Tutorial 1 PBP](https://pbp.cs.ui.ac.id/tutorial/tutorial-1.html).

## Struktur dan penjelasan file

```text
myportofolio/
├── manage.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── img/adinata.jpg
└── portofolio/
    ├── settings.py
    ├── urls.py
    ├── views.py
    ├── wsgi.py
    └── asgi.py
```

| File/folder | Penjelasan singkat |
| --- | --- |
| `manage.py` | Entry point command Django, misalnya `migrate`, `check`, dan `runserver`. |
| `portofolio/settings.py` | Konfigurasi aplikasi: environment variables, database SQLite/PostgreSQL, template, static files, WhiteNoise, dan `ALLOWED_HOSTS`. |
| `portofolio/urls.py` | Mendefinisikan URL `/` untuk landing page dan `/admin/` untuk admin Django. |
| `portofolio/views.py` | Berisi `landing_page`, view yang merender `index.html`. |
| `templates/index.html` | Struktur HTML halaman portofolio: header, profil, informasi akademik, tautan sosial, dan footer. |
| `static/css/style.css` | Tampilan halaman: palet warna, grid profil, tombol sosial, serta layout responsif untuk layar kecil. |
| `static/img/adinata.jpg` | Foto profil yang ditampilkan pada landing page. |
| `portofolio/wsgi.py` | Entry point aplikasi untuk server WSGI seperti Gunicorn. |
| `portofolio/asgi.py` | Entry point aplikasi untuk server ASGI. |
| `requirements.txt` | Daftar dependency Python proyek. |
| `.gitignore` | Mencegah environment, database lokal, static build, dan file rahasia ikut ter-commit. |

## Pemeriksaan cepat

Jalankan pemeriksaan konfigurasi Django sebelum commit atau deployment:

```bash
python manage.py check
```

## Refleksi

### Tugas 1

1. Saya menggunakan elemen HTML5 semantik seperti: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan `<footer>` supaya struktur halaman portfolio saya mudah dipahami. For example, setiap bagian About, Skills, dan Experience dibungkus dalam `section`, sedangkan di setiap kartu skill dan pengalaman, saya menggunakan `article`. Dengan struktur ini membuat kode lebih rapi, memudahkan pembaca dan screen reader mengenali fungsi setiap bagian, serta membantu pemeliharaan halaman ketika kontennya bertambah.

2. Tantangan utama dalam membuat layout responsif adalah mengubah tampilan desktop yang memiliki hero dua kolom dan grid tiga kartu skill menjadi tetap nyaman dibaca pada layar kecil. Saya memprioritaskan informasi identitas, foto profil, skill, lalu pengalaman. Pada ukuran layar maksimal 600px, layout hero dan grid skill diubah menjadi satu kolom, ukuran teks disesuaikan, dan jarak antar-elemen dirapikan agar pengguna mobile tidak perlu melakukan zoom atau scroll horizontal.

3. Keterbatasan website statis ini adalah seluruh isi portfolio masih ditulis langsung atau di hardcode di file HTML. Saat ingin memperbarui skill atau pengalaman, saya harus mengubah kode dan melakukan deployment ulang, pengguna juga belum dapat mengirim data atau berinteraksi dengan sistem. Fitur dinamis yang ingin saya tambahkan berikutnya adalah model Django dan Django Admin untuk mengelola data project, skill, dan pengalaman tanpa mengedit HTML, serta form kontak yang dapat menyimpan atau mengirim pesan dari pengunjung.
