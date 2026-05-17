# 🏢 Gelişmiş CardWell CRM Sistemi (Profesyonel Versiyon)

Arka uç (Backend) performans gücü ile modern arayüz (Frontend) estetiğini birleştiren kapsamlı bir Müşteri İlişkileri Yönetimi (CRM) sistemidir. Bu proje, **Python** dili kullanılarak, Nesne Yönelimli Programlama (OOP) prensipleri ve en güncel tasarım teknikleri odak alınarak inşa edilmiştir.

> **⚠️ Eğitim Amaçlı Proje:** Bu yazılım tamamen **eğitim amaçlı** geliştirilmiş olup, modern bir CRM sisteminin mimarisini ve entegrasyon süreçlerini öğretmeyi hedeflemektedir.

## ✨ Ana Özellikler

### 1. Çoklu Kullanıcı Arayüzleri (UI/UX)
*   **Profesyonel PyQt5 Arayüzü (`gui.py`):** Kapsamlı bir kontrol paneli, müşteri yönetimi, satış takibi ve teknik destek sistemi sunan modern "Glassmorphism" tarzı arayüz.
*   **Gelecek Nesil CustomTkinter Arayüzü (`cardwell_crm.py`):** Nakit akışı ve görsel istatistiklere odaklanan ultra modern gösterge paneli (Dashboard).

### 2. Veri Yönetimi ve Doğrulama (Data Logic)
*   **SQLAlchemy Veritabanı:** Veri kararlılığını ve hızını sağlamak için JSON dosyalarından gerçek bir **SQLite** veritabanına geçiş yapılmıştır.
*   **Pydantic ile Doğrulama:** Veritabanı temizliğini sağlamak için giriş verilerinde (e-posta formatı, telefon numaraları, negatif fiyatların önlenmesi gibi) katı doğrulama sistemi.
*   **Rapor Dışa Aktarma:** Harici analizler için satış ve müşteri verilerini **Excel** dosyalarına dönüştürme imkanı.

### 3. Fonksiyonel Bölümler
*   **Müşteri Bölümü:** Müşteri geçmişi, toplam harcama ve açık sipariş sayısı takibi.
*   **Satış Bölümü:** Oluşturmadan tamamlanmaya veya iptale kadar satış süreçlerinin yönetimi.
*   **Yardım Merkezi (Support):** Çözüm süresinin otomatik hesaplandığı, müşteri sorunlarını takip eden destek talebi (ticket) sistemi.

## 📧 E-posta Servisi (Email Service)

Müşterilerle sürekli ve profesyonel iletişim sağlamak için otomatik bir bildirim sistemi entegre edilmiştir:
*   **Hoş Geldin Mesajları:** Profesyonel bir izlenim bırakmak için sisteme yeni bir müşteri eklendiğinde otomatik olarak gönderilir (`send_welcome`).
*   **Satış Onayı:** Yeni bir satın alma işlemi kaydedildiğinde, ürün adı ve fiyatını içeren detaylı bildirim gönderilir (`send_sale_confirmation`).
*   **Talep Güncellemeleri:** Yeni bir destek talebi açıldığında veya durumu değiştiğinde (örneğin "Çözüldü" olarak işaretlendiğinde) müşteriyi bilgilendirmek için e-posta gönderilir (`send_ticket_update`).

> **⚙️ Servis Kurulumu:** Gerçek gönderimi etkinleştirmek için `email_service.py` dosyasını açmalı, SMTP sunucu bilgilerinizle (Gmail veya Outlook gibi) yapılandırmalı, e-posta adresinizi ve Uygulama Şifrenizi (App Password) eklemelisiniz.

## 🚀 Proje Teknolojileri (Stack)

*   **Core:** Python 3.13
*   **GUI:** PyQt5 & CustomTkinter
*   **Validation:** Pydantic (v2)
*   **Database:** SQLAlchemy (ORM) & SQLite
*   **Data Analysis:** Pandas
*   **Mailing:** SMTPLib

## 📂 Dosya Yapısı

*   `gui.py`: Ana grafik arayüzü (PyQt5) ve ilgili mantık.
*   `cardwell_crm.py`: Modern gösterge paneli arayüzü (CustomTkinter).
*   `controller.py`: Arayüzler ile veritabanı arasında bağlantı kuran arka uç (Backend) motoru.
*   `crm_console.py`: Pydantic mantığıyla çalışan komut satırı (Console) sürümü.
*   `email_service.py`: E-posta taslaklarını oluşturup göndermekten sorumlu modül.





-----------------------------------------------------------------------------
* öğrenim amajlı geliştirilmiştir *
