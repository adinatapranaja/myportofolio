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

### Tutorial 2 — Implementasi Model-View-Template (MVT)

Tutorial 2 mengubah portfolio statis menjadi aplikasi Django dengan pola Model-View-Template. Aplikasi `main` menyimpan model `Experience`; view mengambil data dan mengirimkannya melalui context; lalu template menampilkan profil pada `/` dan daftar pengalaman dinamis pada `/experience/`. Tutorial ini juga menambahkan migration, URL namespace, navigasi dengan tag `{% url %}`, serta enam unit test untuk model dan halaman aplikasi.

Sumber: [Tutorial 2 PBP](https://pbp.cs.ui.ac.id/tutorial/tutorial-2.html).

## Fitur Tugas 2 — Projects

Tugas 2 menambahkan halaman **Projects** pada URL `/projects/`. Halaman ini mengambil seluruh data dari model `Project` dan menampilkannya secara dinamis menggunakan perulangan Django Template Language. Setiap proyek dapat memiliki judul, deskripsi, teknologi yang digunakan, tautan live project, dan tautan repository. Jika belum ada data, halaman menampilkan pesan empty state.

Untuk menambahkan data proyek lokal melalui Django shell:

```bash
python manage.py shell
```

```python
from main.models import Project

Project.objects.create(
    title="Sistem Kehadiran Event",
    description="Platform kehadiran event dengan QR aman dan dashboard.",
    technologies="Django, Firebase, JavaScript",
    project_url="https://example.com/project",
    repository_url="https://github.com/username/repository",
)
```

## Struktur dan penjelasan file

```text
myportofolio/
├── manage.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── experience.html
│   └── projects.html
├── static/
│   ├── css/style.css
│   └── img/adinata.jpg
├── main/
│   ├── migrations/0001_initial.py
│   ├── migrations/0002_project.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── portofolio/
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
```

| File/folder | Penjelasan singkat |
| --- | --- |
| `manage.py` | Entry point command Django, misalnya `migrate`, `check`, dan `runserver`. |
| `portofolio/settings.py` | Konfigurasi aplikasi: environment variables, database SQLite/PostgreSQL, template, static files, WhiteNoise, dan `ALLOWED_HOSTS`. |
| `portofolio/urls.py` | Menghubungkan URL project ke `main.urls` dan menyediakan route `/admin/`. |
| `main/models.py` | Mendefinisikan model `Experience` dan `Project` sebagai data portfolio dinamis. |
| `main/views.py` | Berisi view halaman profil, experience, dan projects. |
| `main/urls.py` | Mendefinisikan named route untuk `/`, `/experience/`, dan `/projects/`. |
| `main/migrations/0001_initial.py` | Migration awal yang membuat tabel database untuk model `Experience`. |
| `main/migrations/0002_project.py` | Migration yang membuat tabel database untuk model `Project`. |
| `main/tests.py` | Sembilan unit test untuk route, model, tampilan data, dan empty state pada Experience serta Projects. |
| `templates/index.html` | Struktur HTML halaman profil yang menerima data profil dari context view. |
| `templates/experience.html` | Menampilkan daftar objek `Experience` secara dinamis menggunakan Django Template Language. |
| `templates/projects.html` | Menampilkan daftar objek `Project` secara dinamis menggunakan Django Template Language. |
| `static/css/style.css` | Tampilan halaman: palet warna, grid profil, kartu experience/projects, status, empty state, dan layout responsif. |
| `static/img/adinata.jpg` | Foto profil yang ditampilkan pada landing page. |
| `portofolio/wsgi.py` | Entry point aplikasi untuk server WSGI seperti Gunicorn. |
| `portofolio/asgi.py` | Entry point aplikasi untuk server ASGI. |
| `requirements.txt` | Daftar dependency Python proyek. |
| `.gitignore` | Mencegah environment, database lokal, static build, dan file rahasia ikut ter-commit. |

## Pemeriksaan cepat

Jalankan pemeriksaan konfigurasi dan seluruh unit test sebelum commit atau deployment:

```bash
python manage.py check
python manage.py test
```

## Refleksi

### Tugas 1

1. Saya menggunakan elemen HTML5 semantik seperti: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan `<footer>` supaya struktur halaman portfolio saya mudah dipahami. For example, setiap bagian About, Skills, dan Experience dibungkus dalam `section`, sedangkan di setiap kartu skill dan pengalaman, saya menggunakan `article`. Dengan struktur ini membuat kode lebih rapi, memudahkan pembaca dan screen reader mengenali fungsi setiap bagian, serta membantu pemeliharaan halaman ketika kontennya bertambah.

2. Tantangan utama dalam membuat layout responsif adalah mengubah tampilan desktop yang memiliki hero dua kolom dan grid tiga kartu skill menjadi tetap nyaman dibaca pada layar kecil. Saya memprioritaskan informasi identitas, foto profil, skill, lalu pengalaman. Pada ukuran layar maksimal 600px, layout hero dan grid skill diubah menjadi satu kolom, ukuran teks disesuaikan, dan jarak antar-elemen dirapikan agar pengguna mobile tidak perlu melakukan zoom atau scroll horizontal.

3. Keterbatasan website statis ini adalah seluruh isi portfolio masih ditulis langsung atau di hardcode di file HTML. Saat ingin memperbarui skill atau pengalaman, saya harus mengubah kode dan melakukan deployment ulang, pengguna juga belum dapat mengirim data atau berinteraksi dengan sistem. Fitur dinamis yang ingin saya tambahkan berikutnya adalah model Django dan Django Admin untuk mengelola data project, skill, dan pengalaman tanpa mengedit HTML, serta form kontak yang dapat menyimpan atau mengirim pesan dari pengunjung.

### Tugas 2

1. Ketika pengguna membuka halaman `/projects/`, browser mengirimkan request ke Django. Berkas `portofolio/urls.py` meneruskan request tersebut ke `main/urls.py` melalui `include("main.urls")`. Selanjutnya, route bernama `main:show_projects` memetakan path `projects/` ke view `show_projects`. View mengambil seluruh objek dari model `Project` dengan `Project.objects.all()`, memasukkannya ke dalam context sebagai `project_list`, lalu merender `projects.html`. Template melakukan perulangan terhadap `project_list` dan Django mengembalikan HTML hasil render sebagai response ke browser.

2. Data Projects lebih baik disimpan di model karena data tidak bercampur dengan struktur tampilan HTML. Saya dapat menambah, mengubah, atau menghapus proyek melalui database tanpa menyalin dan mengubah kartu HTML satu per satu. Pemisahan ini juga membuat halaman dapat memperbarui jumlah kartu secara otomatis, lebih mudah diuji, dan dapat dikembangkan ke fitur berikutnya seperti Django Admin, form tambah proyek, atau halaman detail.

3. `makemigrations` membuat berkas migration yang mencatat perubahan pada definisi model, sedangkan `migrate` menerapkan perubahan yang sudah tercatat tersebut ke struktur database. Contohnya, ketika saya menambahkan model `Project` dengan field `title`, `description`, dan `technologies`, saya menjalankan `python manage.py makemigrations` untuk membuat migration `0002_project.py`, kemudian `python manage.py migrate` untuk membuat tabel `Project` di database.

### AI Disclosure
Dalam pengerjaan project ini, saya menggunakan bantuan AI secara terbatas, yaitu untuk membantu merapikan format penulisan pada file README.md agar lebih terstruktur dan mudah dibaca, serta untuk mencari referensi dan tutorial dalam mengembangkan desain web yang saya buat. Seluruh proses pengembangan, logika, dan implementasi tetap saya kerjakan dan pahami sendiri.
