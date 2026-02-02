# Python Backend Case Study - FastAPI Item Management System

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

## ⚙️ Gereksinimler (Prerequisites)

Projeyi çalıştırmadan önce aşağıdaki yazılımların kurulu olduğundan emin olun:

| Yazılım | Minimum Versiyon | İndirme Linki |
|---------|------------------|---------------|
| Docker Desktop | 4.0+ | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Git | 2.0+ | [git-scm.com](https://git-scm.com/) |

> **Not:** Docker Desktop kuruluysa PostgreSQL ve Redis'i ayrıca kurmanıza gerek yok - Docker bunları otomatik indirir.

---

## 🛠️ Kurulum (Setup)

### 1. Projeyi Klonlayın

```bash
git clone https://github.com/habipokc/case-study-backend-v1.git
cd case-study-backend-v1
```

### 2. Çevresel Değişkenler (.env)

```bash
# Linux/Mac:
cp .env.example .env

# Windows (PowerShell):
Copy-Item .env.example .env

# Windows (CMD):
copy .env.example .env
```

> **Önemli:** `.env` dosyasını düzenlemenize gerek yok, varsayılan değerler Docker ortamı için çalışacaktır.

### 3. Docker ile Çalıştırma ✨

```bash
docker-compose up --build
```

İlk çalıştırmada image'lar indirilecek (5-10 dk sürebilir). Başarılı olduğunda şu mesajı göreceksiniz:
```
web-1    | INFO:     Uvicorn running on http://0.0.0.0:8000
web-1    | Redis connected successfully.
```

### 4. Veritabanı Migration (İlk Kurulumda Gerekli)

Yeni bir terminal açın ve çalıştırın:

```bash
docker-compose exec web alembic upgrade head
```

### 5. Test Edin

Tarayıcınızda açın: **http://localhost:8000/docs**

---

## 📚 API Dokümantasyonu

| URL | Açıklama |
|-----|----------|
| http://localhost:8000/docs | Swagger UI (Interaktif) |
| http://localhost:8000/redoc | ReDoc (Okunabilir) |
| http://localhost:8000/health | Health Check |

---

## 🧪 Testler

```bash
# Docker container içinde testleri çalıştır
docker-compose exec web pytest

# Coverage raporu ile
docker-compose exec web pytest --cov=app --cov-report=term-missing
```

**Test Coverage:** %79 ✅

---

## 📡 Endpoint Listesi

### Auth (User Management)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/api/v1/users/register` | Yeni kullanıcı kaydı |
| POST | `/api/v1/users/login` | Giriş yap ve JWT al |
| POST | `/api/v1/users/logout` | Çıkış yap (Token blacklist) |
| POST | `/api/v1/users/refresh` | Access token yenile |

### Users (Profile)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/v1/users/profile` | Profil bilgilerini getir |
| PUT | `/api/v1/users/profile` | Profil güncelle |

### Items
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/v1/items/` | Ürünleri listele |
| POST | `/api/v1/items/` | Yeni ürün ekle |
| GET | `/api/v1/items/{id}` | Detay görüntüle |
| PUT | `/api/v1/items/{id}` | Güncelle |
| DELETE | `/api/v1/items/{id}` | Sil (Soft Delete) |

### Analytics
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/v1/items/analytics/category-density` | Kategori yoğunluk raporu |

**Query Parameters (GET /items):**
- `page`: Sayfa numarası (default: 1)
- `per_page`: Sayfa başına kayıt (default: 10, max: 100)
- `category`: Kategori filtresi
- `status`: Durum filtresi (active/inactive/draft)
- `sort_by`: Sıralama alanı (created_at/name/category)
- `order`: Sıralama yönü (asc/desc)

---

## 🔥 Örnek API Kullanımı

### 1. Kullanıcı Kaydı
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret123", "first_name": "John", "last_name": "Doe"}'
```

### 2. Giriş Yap
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -d "username=test@example.com&password=secret123"
```

### 3. Item Oluştur (Token ile)
```bash
curl -X POST http://localhost:8000/api/v1/items/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "category": "electronics", "status": "active"}'
```

---

## 🔐 Güvenlik

- **JWT Authentication:** Access token (1 saat) + Refresh token (7 gün)
- **Password Hashing:** bcrypt algoritması
- **Token Revocation:** Redis Blacklist ile logout
- **Environment Security:** Hassas veriler `.env` dosyasında

---

## 🏗️ Proje Yapısı

```
├── app/
│   ├── api/              # API Router ve Endpoint'ler
│   │   └── v1/endpoints/ # Versioned endpoints
│   ├── core/             # Config, Security, Database, Redis
│   ├── models/           # SQLAlchemy Modelleri
│   ├── repositories/     # Data Access Layer
│   ├── schemas/          # Pydantic Şemaları
│   ├── services/         # Business Logic
│   └── main.py           # FastAPI App Entry
├── tests/                # Pytest Test Senaryoları
├── alembic/              # DB Migrasyonları
├── docker-compose.yml    # Docker Orchestration
├── Dockerfile            # Multi-stage Build
└── requirements.txt      # Python Dependencies
```

---

## 🛑 Troubleshooting

### Docker port hatası
```
Error: Port 5432 already in use
```
**Çözüm:** Yerel PostgreSQL'i durdurun veya `docker-compose.yml`'de portu değiştirin.

### Redis bağlantı hatası
```
Redis connection refused
```
**Çözüm:** Docker container'larının çalıştığından emin olun: `docker-compose ps`

### Migration hatası
```
alembic.util.exc.CommandError
```
**Çözüm:** Veritabanını sıfırlayın: 
```bash
docker-compose down -v
docker-compose up --build
docker-compose exec web alembic upgrade head
```

---

## 📋 Hızlı Başlangıç Checklist

- [ ] Docker Desktop kurulu ve çalışıyor
- [ ] `git clone` ile proje indirildi
- [ ] `.env` dosyası oluşturuldu
- [ ] `docker-compose up --build` çalıştırıldı
- [ ] `alembic upgrade head` migration yapıldı
- [ ] http://localhost:8000/docs açılıyor

---

## 📄 Lisans

MIT License
