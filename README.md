# 🚌 Ottobus - Sistem Pemesanan Tiket Bus Online

![Ottobus Banner](https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=1200&h=400&fit=crop)

Sistem pemesanan tiket bus online berbasis web dengan fitur lengkap untuk pengguna dan admin. Dibangun menggunakan Python (Backend) dan HTML/TailwindCSS (Frontend).

---

## 📋 Informasi Proyek

| Item | Detail |
|------|--------|
| **Nama** | Kiky Restu Noviansyah |
| **NIM** | 1123102110 |
| **Mata Kuliah** | Pemrograman Frontend & Backend |
| **Semester** | 3 |

---

## ✨ Fitur Utama

### 🎫 Fitur Pengguna
- ✅ Pencarian rute bus (asal, tujuan, tanggal)
- ✅ Lihat detail bus dan fasilitas
- ✅ Pilih kursi secara visual
- ✅ Halaman profil pengguna
- ✅ E-Wallet (OttoPay) - saldo digital
- ✅ Riwayat pemesanan tiket
- ✅ Registrasi & Login

### 🔧 Fitur Admin
- ✅ Dashboard statistik
- ✅ Kelola Jadwal (CRUD)
- ✅ Kelola Bus (CRUD)
- ✅ Kelola Perusahaan (CRUD)
- ✅ Kelola Konten Website
- ✅ Upload gambar bus

### 📱 Mobile Responsive
- ✅ Tampilan mobile-first
- ✅ Bottom Navigation (Mobile)
- ✅ Search widget ala RedBus
- ✅ Quick date selection (Today/Tomorrow)

---

## 🔐 Kredensial Login

### Admin Panel (`/admin`)
| Username | Password |
|----------|----------|
| `admin` | `admin123` |

### User (`/login.html`)
| Email | Password |
|-------|----------|
| `demo@ottobus.com` | `demo123` |

> 💡 **Tip:** Anda juga bisa mendaftar akun baru melalui halaman Register

---

## 🛠️ Teknologi yang Digunakan

| Layer | Teknologi |
|-------|-----------|
| **Frontend** | HTML5, TailwindCSS, JavaScript |
| **Backend** | Python 3.x (http.server) |
| **Database** | SQLite3 |
| **Icons** | Lucide Icons |
| **Fonts** | Google Fonts (Inter) |

---

## 🚀 Cara Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/kikyrestu/UAS-Frontend-Backend-SMT3-Kiky-Restu-Noviansyah-1123102110.git
cd UAS-Frontend-Backend-SMT3-Kiky-Restu-Noviansyah-1123102110
```

### 2. Jalankan Server
```bash
python server.py
```

### 3. Buka Browser
```
http://localhost:8000
```

---

## 📁 Struktur Folder

```
📦 FRONTEND
 ┣ 📂 admin/           # Halaman Admin Panel
 ┃ ┣ 📜 index.html     # Dashboard Admin
 ┃ ┗ 📜 login.html     # Login Admin
 ┣ 📂 uploads/         # Folder upload gambar
 ┣ 📜 index.html       # Landing Page
 ┣ 📜 buses.html       # Daftar Jadwal Bus
 ┣ 📜 bus-detail.html  # Detail Bus
 ┣ 📜 select-seat.html # Pilih Kursi
 ┣ 📜 login.html       # Login User
 ┣ 📜 register.html    # Registrasi User
 ┣ 📜 profile.html     # Profil User + E-Wallet
 ┣ 📜 history.html     # Riwayat Pemesanan
 ┣ 📜 server.py        # Backend Server Python
 ┗ 📜 ottobus.db       # Database SQLite
```

---

## 📊 Database Schema

### Tabel Utama
| Tabel | Deskripsi |
|-------|-----------|
| `users` | Data pengguna (termasuk wallet_balance) |
| `companies` | Data perusahaan bus |
| `buses` | Data armada bus |
| `schedules` | Jadwal keberangkatan |
| `bookings` | Riwayat pemesanan |
| `content` | Konten dinamis website |

---

## 📸 Screenshots

### Landing Page
![Landing Page](https://via.placeholder.com/800x400?text=Landing+Page)

### Admin Dashboard
![Admin Dashboard](https://via.placeholder.com/800x400?text=Admin+Dashboard)

### Mobile View
![Mobile View](https://via.placeholder.com/400x800?text=Mobile+View)

---

## 📝 Catatan Pengembangan

- Database akan otomatis dibuat saat server pertama kali dijalankan
- Data demo (jadwal, bus, user) akan di-seed otomatis
- Saldo E-Wallet default: Rp 500.000
- Fitur checkout/pembayaran masih dalam pengembangan

---

## 👨‍💻 Author

**Kiky Restu Noviansyah**  
NIM: 1123102110  
Teknik Informatika - Universitas Telkom

---

## 📄 License

This project is created for educational purposes only.

© 2024-2026 Ottobus. All rights reserved.
