# Backlink Panel

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

Backlink Panel, web sitelerinin backlink profillerini yönetmek ve analiz etmek için geliştirilmiş kapsamlı bir web uygulamasıdır. SEO çalışmalarınızı optimize etmek ve backlink stratejinizi geliştirmek için güçlü araçlar sunar.

## 🚀 Özellikler

- Backlink profili analizi
- Detaylı raporlama sistemi
- Backlink kalite değerlendirmesi
- Otomatik link takibi
- SEO metriklerinin izlenmesi
- Çoklu domain yönetimi

## 📋 Gereksinimler

- Python 3.8+
- Docker
- Web sunucusu (Apache/Nginx)
- PostgreSQL

## 🛠️ Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/MrTurcoSoft/backlink_panel.git
cd backlink_panel
```

2. Docker ile kurulum:
```bash
docker-compose up -d
```

3. Gerekli bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## 🔧 Yapılandırma

`config.yaml` dosyasını düzenleyerek temel ayarları yapılandırabilirsiniz:

```yaml
database:
  host: localhost
  port: 5432
  name: backlink_db
  user: user
  password: password

server:
  port: 5000
  debug: false
```

## 📖 Kullanım

1. Sunucuyu başlatın:
```bash
python manage.py runserver
```

2. Tarayıcınızda aşağıdaki adresi açın:
```
http://localhost:5000
```

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylı bilgi için [LICENSE](LICENSE) dosyasına bakınız.

## 📞 İletişim

MrTurcoSoft - [@MrTurcoSoft](https://github.com/MrTurcoSoft)

Proje Linki: [https://github.com/MrTurcoSoft/backlink_panel](https://github.com/MrTurcoSoft/backlink_panel)
