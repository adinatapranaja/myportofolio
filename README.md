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

### Tutorial 3 — Form dan Data Delivery

Tutorial 3 menambahkan `base.html` sebagai skeleton agar navbar dan footer digunakan ulang oleh seluruh halaman. Data Project kini dapat ditambahkan melalui form di `/projects/add/` yang memakai `ModelForm` dan CSRF token. Aplikasi juga menyediakan endpoint JSON di `/api/projects/`, termasuk filter judul melalui query `?title=`, lalu halaman `/projects/` menampilkan hasilnya. Terakhir, halaman Project mendapat fitur pencarian serta dialog konfirmasi untuk menghapus data dengan request POST yang terlindungi CSRF.

Sumber: [Tutorial 3 PBP](https://pbp.cs.ui.ac.id/tutorial/tutorial-3.html).

### Tutorial 4 — Authentication, Session, dan Cookies

Tutorial 4 menambahkan autentikasi bawaan Django melalui halaman Register, Login, dan Logout. Setelah login, Django menyimpan identitas pengguna dalam session dan aplikasi menyimpan cookie `last_login` untuk menampilkan waktu login terakhir. Tutorial ini juga menerapkan otorisasi: hanya superuser yang dapat membuat atau menghapus Project, sedangkan user yang sudah login dapat memberi atau membatalkan star pada Project.

Sumber: [Tutorial 4 PBP](https://pbp.cs.ui.ac.id/tutorial/tutorial-4.html).

### Tutorial 5 — Web Interactivity with JavaScript

Halaman Projects memuat data melalui Fetch API dari `/api/projects/`, termasuk jumlah star dan status star pengguna saat ini. Pencarian menggunakan debounce 300 ms, membatalkan request lama, dan menyediakan status loading, kosong, serta gagal.

Superuser dapat menambahkan proyek melalui modal dengan POST AJAX ke `/projects/add-ajax/`. Endpoint memakai `ProjectForm`, pemeriksaan hak akses, dan CSRF. Saat berhasil, modal ditutup, daftar diperbarui mengikuti pencarian aktif, dan toast ditampilkan. Saat gagal, input tetap tersedia dan toast menampilkan kesalahan.

Data kartu diisi menggunakan `textContent`, bukan interpolasi ke `innerHTML`; tautan hanya menerima HTTP/HTTPS. `ProjectForm` menghapus tag pada judul, deskripsi, dan teknologi, serta menolak judul yang kosong setelah dibersihkan. Pembersihan server berlaku pada tambah biasa, tambah AJAX, dan edit. `strip_tags` bukan pengganti render aman dan tidak mengubah data lama; teks seperti `List<String>` juga dapat terpotong.

Star dan hapus masih menggunakan POST biasa. Kontrol edit tetap tersedia bagi Editor dan superuser. Kode interaksi terdapat pada `static/js/projects.js`, sedangkan toast pada `static/js/toast.js`.

Sumber: [Tutorial 5 PBP](https://pbp.cs.ui.ac.id/tutorial/tutorial-5.html)

### Tutorial 7 — Implementasi Django REST Framework

Tutorial 7 membangun ulang API Projects dengan Django REST Framework (DRF) 3.18. Model `Project` dan datanya tetap sama; yang berubah adalah cara data dikirim dan diterima.

| Kebutuhan | Tutorial 5 (manual) | Tutorial 7 (DRF) |
| --- | --- | --- |
| Objek menjadi JSON | Dictionary dirakit dalam loop | `ProjectSerializer` |
| Validasi input | `ProjectForm` | Method `validate_*` pada serializer |
| Hak akses | `if` di dalam view | Permission class |
| Method yang diizinkan | `@require_POST` | `@api_view([...])` |
| Response | `JsonResponse` | `Response` (JSON atau Browsable API) |

Kontrak API baru berada di bawah prefix `/api/v1/`:

| Method | Endpoint | Tindakan | Siapa yang boleh |
| --- | --- | --- | --- |
| GET | `/api/v1/projects/?title=` | Daftar dan pencarian | Semua pengunjung |
| POST | `/api/v1/projects/` | Tambah proyek | Superuser |
| GET | `/api/v1/projects/<uuid>/` | Detail proyek | Semua pengunjung |
| PUT / PATCH | `/api/v1/projects/<uuid>/` | Ubah proyek | Superuser |
| DELETE | `/api/v1/projects/<uuid>/` | Hapus proyek (204) | Superuser |
| POST | `/api/v1/projects/<uuid>/star/` | Beri/batalkan star | Pengguna login |

Autentikasi memakai `SessionAuthentication`, sehingga login portofolio yang sudah ada tetap dipakai dan setiap request tulis wajib membawa token CSRF. `IsPortfolioOwnerOrReadOnly` mengizinkan baca untuk semua orang dan tulis hanya untuk `is_superuser` (bukan `is_staff`). Endpoint star memakai `IsAuthenticated`, dan akun pemberi star selalu diambil dari `request.user`. Field `star_count`, `is_starred`, dan `starred_by_names` dihitung server dan tidak dapat diisi klien.

`ProjectSerializer` tidak menjalankan `ProjectForm`, sehingga pembersihan `strip_tags` dan penolakan judul kosong ditulis ulang pada serializer. `URLField` tetap menolak skema seperti `javascript:`.

Halaman `/projects/` kini memuat, menambah, memberi star, dan menghapus data melalui API DRF tanpa reload. Kontrak data berubah dari `item.pk`/`item.fields.title` menjadi `item.id`/`item.title`, dan error validasi berbentuk `{"title": ["..."]}`. Fungsi `writeProject` di `static/js/projects.js` menangani JSON, header `X-CSRFToken`, dan response 204 secara konsisten. Kartu tetap diisi dengan `textContent` dan tautan tetap dibatasi ke HTTP/HTTPS. Tamu melihat tautan "Login to star", sedangkan modal konfirmasi hapus kini mengirim DELETE. Halaman edit HTML untuk Editor dan endpoint lama (`/api/projects/`, `/projects/add-ajax/`) tidak dihapus.

`IsPortfolioOwnerOrEditorOrReadOnly` disiapkan untuk bagian pilihan tugas: Editor boleh PUT/PATCH, sedangkan POST dan DELETE tetap khusus superuser.

Pengujian API berada di `main/tests_api.py`: 13 test dari tutorial untuk akses publik, pencarian, 404, permission tiap peran, validasi, PATCH/PUT/DELETE, star, field read-only, method salah, dan CSRF dengan session sungguhan, ditambah test matriks peran untuk permission Editor.

```bash
python manage.py test main.tests_api --verbosity 2
python manage.py test main
```

Untuk mencoba API di browser, jalankan server lalu buka `/api/v1/projects/`. Login melalui `/login/` atau `/api-auth/login/`, dan tambahkan `?format=json` untuk melihat JSON mentah.

Sumber: [Tutorial 7 PBP](https://pbp.cs.ui.ac.id/tutorial/tutorial-7.html)

## Struktur dan penjelasan file

```text
myportofolio/
├── manage.py
├── requirements.txt
├── templates/
│   ├── components/project_delete_modal.html
│   ├── base.html
│   ├── create_project.html
│   ├── index.html
│   └── experience.html
├── static/
│   ├── css/style.css
│   ├── img/adinata.jpg
│   └── js/projects.js
├── main/
│   ├── migrations/0001_initial.py
│   ├── migrations/0002_project.py
│   ├── api_urls.py
│   ├── api_views.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── tests_api.py
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
| `portofolio/settings.py` | Konfigurasi aplikasi: environment variables, database SQLite/PostgreSQL, template, static files, WhiteNoise, `ALLOWED_HOSTS`, dan `CSRF_TRUSTED_ORIGINS` untuk PWS. |
| `portofolio/urls.py` | Menghubungkan URL project ke `main.urls`, API DRF di `/api/v1/`, login Browsable API di `/api-auth/`, dan route `/admin/`. |
| `main/models.py` | Mendefinisikan model database `Experience` dan `Project`. |
| `main/forms.py` | `ProjectForm` berbasis `ModelForm` untuk memvalidasi serta menyimpan Project dari halaman form. |
| `main/views.py` | View halaman profil, pengalaman, Project, autentikasi, form, JSON API, star, dan pemeriksaan hak akses. |
| `main/urls.py` | Mendefinisikan route halaman, autentikasi, pengelolaan portfolio, JSON API, dan star Project. |
| `main/serializers.py` | `ProjectSerializer` untuk representasi JSON, validasi input API, dan field star hasil perhitungan. |
| `main/permissions.py` | Permission DRF: tulis khusus superuser, serta varian yang mengizinkan Editor melakukan PUT/PATCH. |
| `main/api_views.py` | API view DRF untuk daftar/tambah, detail/ubah/hapus, dan star Project. |
| `main/api_urls.py` | Route API dengan namespace `api`, misalnya `api:project-list`. |
| `main/tests_api.py` | Test API DRF untuk permission, validasi, star, method, dan CSRF. |
| `static/js/projects.js` | Memuat, mencari, menambah, memberi star, dan menghapus Project melalui API DRF. |
| `main/migrations/` | Riwayat perubahan struktur database untuk model `Experience` dan `Project`, termasuk data seed portfolio. |
| `main/tests.py` | Unit test untuk route, model, form tambah, JSON API/filter, serta hapus Project. |
| `templates/base.html` | Skeleton bersama yang memuat metadata, navbar, footer, dan blok konten halaman. |
| `templates/index.html` | Struktur HTML halaman profil yang menerima data profil dari context view. |
| `templates/experience.html` | Menampilkan daftar objek `Experience` secara dinamis menggunakan Django Template Language. |
| `templates/projects.html` | Menampilkan Project, form pencarian berdasarkan judul, dan kontrol tambah/hapus Project. |
| `templates/create_project.html` | Halaman form untuk menambahkan Project baru. |
| `templates/register.html` dan `templates/login.html` | Halaman autentikasi memakai form bawaan Django. |
| `templates/edit_project.html` | Halaman untuk memperbarui Project oleh Editor atau superuser. |
| `templates/components/project_star.html` | Komponen form POST untuk memberi atau membatalkan star pada Project. |
| `templates/components/project_delete_modal.html` | Komponen dialog konfirmasi sebelum sebuah Project dihapus. |
| `static/css/style.css` | Tampilan halaman, form Project, pencarian, dialog hapus, serta layout responsif. |
| `static/img/adinata.jpg` | Foto profil yang ditampilkan pada landing page. |
| `portofolio/wsgi.py` | Entry point aplikasi untuk server WSGI seperti Gunicorn. |
| `portofolio/asgi.py` | Entry point aplikasi untuk server ASGI. |
| `requirements.txt` | Daftar dependency Python proyek. |
| `.gitignore` | Mencegah environment, database lokal, static build, dan file rahasia ikut ter-commit. |

## Pemeriksaan cepat

Jalankan pemeriksaan konfigurasi dan seluruh unit test sebelum commit atau deployment:

```bash
python manage.py check
python manage.py test main
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

### Tugas 3

1. `ModelForm` digunakan karena Django dapat membentuk field form berdasarkan model, menjalankan validasi yang sesuai dengan tipe field model, dan menyimpan data melalui `form.save()`. Pendekatan ini mengurangi boilerplate serta menjaga form tetap selaras saat model berubah. `{% csrf_token %}` wajib ada pada form yang mengubah data karena Django memverifikasi token tersebut untuk memastikan request POST benar-benar berasal dari halaman aplikasi yang sah, bukan dari situs lain yang mencoba melakukan *cross-site request forgery*.

2. JSON lebih disukai pada aplikasi web modern karena lebih ringkas daripada XML, mudah dibaca, dan diproses secara native oleh JavaScript. JSON cocok untuk struktur objek dan array yang umum dipakai oleh REST API, sedangkan XML membutuhkan banyak tag pembuka/penutup sehingga ukuran payload serta proses parsing biasanya lebih besar.

3. Saat endpoint `/api/experiences/` diakses, Django memanggil `get_experiences_json`, mengambil queryset `Experience`, lalu mengubahnya menggunakan `serializers.serialize("json", experiences)`. Respons dikirim dengan `content_type="application/json"`. Serialisasi diperlukan karena objek model Django—termasuk UUID dan field tanggal—bukan objek JSON bawaan. Pada halaman Experience, respons tersebut dideserialisasi kembali agar template dapat bekerja dengan objek `Experience`.

### Tugas 4

#### Konfigurasi role Editor

1. Jalankan `python manage.py createsuperuser` bila belum memiliki akun pemilik portfolio.
2. Login ke `/admin/` menggunakan akun superuser tersebut.
3. Pada menu **Groups**, buat group bernama tepat `Editor`.
4. Pada menu **Users**, buka akun yang ingin dijadikan editor lalu tambahkan group `Editor` pada bagian Groups.

Hak akses aplikasi adalah sebagai berikut:

| Role | Lihat data | Star Project | Tambah | Edit | Hapus |
| --- | --- | --- | --- | --- | --- |
| Guest | Ya | Redirect ke login | Redirect ke login | Redirect ke login | Redirect ke login |
| User biasa | Ya | Ya | 403 | 403 | 403 |
| Editor | Ya | Ya | 403 | Ya | 403 |
| Superuser | Ya | Ya | Ya | Ya | Ya |

Project memakai relasi `ManyToManyField` ke `User` agar satu pengguna hanya dapat memberi satu star pada Project yang sama. Endpoint `/api/projects/` tetap dapat diakses publik, tetapi relasi star diserialisasi dengan username, bukan ID internal user.

### Tugas 5

Implementasi tugas diterapkan pada **Experience** di `/experience/`. Halaman merender kerangka dan mengambil data melalui `/api/experiences/` menggunakan Fetch API. JSON disusun dengan `JsonResponse`, termasuk jumlah star, status star pengguna, kategori, dan status pengalaman. Pencarian judul menggunakan debounce 300 ms dan `AbortController`, dengan tampilan loading, kosong, serta error.

Superuser dapat membuka modal Add experience dan mengirim form ke `/experience/add-ajax/` tanpa reload. Endpoint memvalidasi `ExperienceForm`, memeriksa hak akses, dan mengembalikan 201 saat berhasil, 400 untuk kesalahan validasi, atau 403 untuk pengguna tanpa izin. CSRF dikirim lewat `FormData` dan header `X-CSRFToken`. Form ditutup dan daftar diperbarui sesuai pencarian aktif setelah berhasil; saat gagal, input tetap tersedia dan toast menampilkan pesan kesalahan.

Pengunjung dapat membaca data. Pengguna yang login dapat memberi atau membatalkan star; Editor dapat mengedit; superuser dapat menambah, mengedit, dan menghapus. Star, edit, dan hapus masih memakai alur request biasa. Operasi tambah AJAX mengembalikan JSON 403 kepada tamu, berbeda dari halaman tambah biasa yang mengarahkan tamu ke login.

Teks kartu diisi dengan `textContent`. Judul dan deskripsi dibersihkan menggunakan `strip_tags` di `ExperienceForm`, dan nilai yang kosong setelah dibersihkan ditolak. Perlindungan ini berlaku pada tambah biasa, tambah AJAX, dan edit. `strip_tags` bukan pengganti render aman dan dapat memotong teks seperti `List<String>`; data lama tetap harus ditampilkan sebagai teks.

#### Setup dan pemeriksaan

Aktifkan environment sesuai instruksi di awal README, lalu jalankan:

```bash
python manage.py migrate
python manage.py check
python manage.py test main
python manage.py runserver
```

Migrasi `0005_experience_starred_by` menambahkan relasi star Experience. Logika browser ada di `static/js/experience.js`, modal ada di `templates/components/experience_form_modal.html`, dan toast menggunakan komponen bersama dari Tutorial 5.

Pengujian otomatis mencakup akses tiap peran, JSON dan filter, star, CSRF, validasi AJAX, serta payload XSS pada tambah dan edit. Pemeriksaan interaksi visual di browser belum selesai karena browser otomatis tidak tersedia. Untuk verifikasi manual:

1. Buka `/experience/` sebagai tamu, user biasa, Editor, dan superuser; pastikan daftar tampil dan kontrol sesuai hak akses.
2. Ketik judul pada pencarian dan amati request di Network setelah jeda 300 ms. Search/Enter harus langsung mencari; pencarian tanpa hasil menampilkan kondisi kosong.
3. Sebagai superuser, tambahkan pengalaman lewat modal. Pastikan tidak ada reload, toast sukses muncul, dan data tampil jika sesuai pencarian aktif.
4. Isi judul hanya dengan spasi atau `<img src="x" onerror="alert('XSS!')">`. Pastikan server menolak, input tetap tersedia, toast error muncul, dan tidak ada alert XSS.
5. Simulasikan koneksi offline melalui DevTools lalu jalankan pencarian untuk memeriksa kondisi error. Aktifkan jaringan kembali dan ulangi pencarian.

#### Jawaban reflektif

1. **Debouncing** menunda pemanggilan fungsi sampai tidak ada input baru selama suatu interval. Pada pencarian Experience, setiap input membatalkan timer sebelumnya dan membuat timer 300 ms. Dengan begitu, browser tidak mengirim request untuk setiap huruf saat pengguna mengetik cepat. Ini mengurangi request dan beban server. Tombol Search/Enter membatalkan timer dan langsung mencari, sedangkan `AbortController` membatalkan request lama agar respons lama tidak menimpa pencarian terbaru.

2. **`await` pada `fetch()`** menunggu Promise selesai sebelum melanjutkan fungsi async tersebut, tanpa memblokir seluruh antarmuka browser. Hasilnya adalah objek `Response`; `await response.json()` kemudian menunggu pembacaan dan parsing body JSON. Tanpa `await`, variabel hasil `fetch()` berisi Promise, sehingga tidak bisa langsung dipakai sebagai `Response`, misalnya dengan memanggil `.json()`. Alternatifnya adalah menggunakan `.then()`. Status HTTP 4xx/5xx tidak otomatis membuat `fetch()` reject, sehingga kode tetap harus memeriksa `response.ok`.

3. **XSS (Cross-Site Scripting)** terjadi ketika data tidak tepercaya ditafsirkan sebagai kode yang dijalankan di browser. Template Django melakukan auto-escaping secara default, sedangkan string JSON yang dimasukkan ke `innerHTML` tidak mendapat perlindungan otomatis tersebut. AJAX sendiri bukan penyebab XSS; cara memasukkan data ke DOM yang menentukan risikonya. Pada Experience, teks dimasukkan lewat `textContent`, sehingga tag ditampilkan sebagai teks, dan input dibersihkan serta divalidasi di server. Validasi URL juga tetap diperlukan karena escaping HTML saja tidak menolak skema seperti `javascript:`.

Sumber: [Individual Assignment 5 PBP](https://pbp.cs.ui.ac.id/assignments/individual/tugas-5.html), berdasarkan salinan HTML yang disimpan.

### AI Disclosure
Dalam pengerjaan project ini, saya menggunakan bantuan AI secara terbatas, yaitu untuk membantu merapikan format penulisan pada file README.md agar lebih terstruktur dan mudah dibaca, serta untuk mencari referensi dan tutorial dalam mengembangkan desain web yang saya buat. Seluruh proses pengembangan, logika, dan implementasi tetap saya kerjakan dan pahami sendiri.
