# 🐍 Python Backend Developer Case Study - FastAPI Item Management System

Bu proje, modern ve ölçeklenebilir bir backend mimarisi (Clean Architecture) kullanılarak geliştirilmiş, Item (Ürün) yönetimi ve analitiği sağlayan bir RESTful API servisidir.

## 🚀 Teknolojiler

- **Python 3.10+**
- **FastAPI:** Yüksek performanslı web framework.
- **PostgreSQL:** Ana veritabanı.
- **SQLAlchemy 2.0 (Async):** Modern Python ORM.
- **Alembic:** Veritabanı migrasyonları.
- **Redis:** Caching ve Token Blacklist.
- **Docker & Docker Compose:** Konteynerizasyon.
- **Pytest:** Otomasyon testleri.
- **Pydantic:** Veri doğrulama ve ayarlar.

---

## 🛠️ Kurulum (Setup)

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin.

### 1. Ön Hazırlık
Ambargoya (Repository) sahip olduğunuzdan emin olun ve dizine gidin:
```bash
git clone https://github.com/habipokc/case-study-backend-v1.git
cd case-study-backend-v1
```

### 2. Çevresel Değişkenler (.env)
Örnek dosyadan bir `.env` dosyası oluşturun:
```bash
cp .env.example .env
```
`.env` dosyasını açın ve gerekli ayarları yapılandırın (Local geliştirme için varsayılanlar yeterlidir).

### 3. Docker ile Çalıştırma (Önerilen) ✨
Tüm sistemi (API + DB) tek komutla ayağa kaldırın:
```bash
docker-compose up --build
```
API şu adreste çalışacak: `http://localhost:8000`

### 4. Yerel Python Ortamı ile Çalıştırma (Alternatif)
Docker kullanmak istemezseniz:

1.  **Sanal Ortam Oluşturun:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: .\venv\Scripts\activate
    ```
2.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Veritabanını Başlatın:** (Yerel bir PostgreSQL sunucunuzun 5432 portunda çalıştığından emin olun).
4.  **Migrasyonları Uygulayın:**
    ```bash
    alembic upgrade head
    ```
5.  **Sunucuyu Başlatın:**
    ```bash
    uvicorn app.main:app --reload
    ```

---

## 📚 Dokümantasyon (Swagger UI)

API başarılı bir şekilde çalıştıktan sonra, interaktif dökümantasyona şuradan erişebilirsiniz:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🧪 Testler

Otomasyon testlerini çalıştırmak ve coverage raporu almak için:

```bash
# Tüm testleri çalıştır
pytest

# Detaylı coverage raporu ile çalıştır
pytest --cov=app --cov-report=term-missing
```
Minimum Hedef Coverage: **%70** (Proje şu an **%79** seviyesindedir).

---

## 📡 Endpoint Listesi

### Auth (User Management)
- `POST /api/v1/users/register`: Yeni kullanıcı kaydı.
- `POST /api/v1/users/login`: Giriş yap ve JWT al.
- `POST /api/v1/users/logout`: Çıkış yap (Token blacklist).
- `POST /api/v1/users/refresh`: Access token yenile.

### Users (Profile)
- `GET /api/v1/users/profile`: Profil bilgilerini getir.
- `PUT /api/v1/users/profile`: Profil güncelle.

### Items
- `GET /api/v1/items/`: Ürünleri listele (Sayfalama: `page`, `per_page`; Filtreleme: `status`, `category`; Sıralama: `sort_by`, `order`).
- `POST /api/v1/items/`: Yeni ürün ekle.
- `GET /api/v1/items/{id}`: Detay görüntüle.
- `PUT /api/v1/items/{id}`: Güncelle.
- `DELETE /api/v1/items/{id}`: Sil (Soft Delete).

### Analytics
- `GET /api/v1/items/analytics/category-density`: Kategori bazlı ürün yoğunluğu raporu.

### System & Health
- `GET /health`: Sistem sağlık durumu kontrolü (Veritabanı bağlantısı dahil).
- `GET /`: API kök dizini (Servis durumunu döner).

---

## 📌 API Versioning
Proje, gelecekteki değişiklikleri yönetmek için URL tabanlı versiyonlama kullanmaktadır.
- Mevcut Versiyon: **v1**
- Base URL: `/api/v1`
- Örnek: `http://localhost:8000/api/v1/items/`

---

## 🔐 Güvenlik
- **Stateless Authentication:** JWT (JSON Web Token) kullanılır.
- **Password Hashing:** Şifreler `bcrypt` ile hashlenerek saklanır.
- **Token Revocation:** Çıkış yapan kullanıcıların tokenları Redis Blacklist ile engellenir.
- **Environment Security:** Hassas veriler `.env` dosyasından okunur, kod içinde saklanmaz.

---

## 🏗️ Proje Yapısı
```
app/
├── api/             # API Router ve Endpoint Tanımları
├── core/            # Config, Security, Database ve Exception Ayarları
├── models/          # SQLAlchemy Veritabanı Modelleri
├── schemas/         # Pydantic Veri Şemaları (Request/Response)
├── services/        # İş Mantığı (Business Logic) Katmanı
└── main.py          # Uygulama Giriş Noktası
tests/               # Pytest Test Senaryoları
alembic/             # Veritabanı Migrasyon Dosyaları
```
