
"""
╔══════════════════════════════════════════════════════════════╗
║       🏢 Basit CRM Sistemi — Customer Relationship Mgmt      ║
║       OOP prensipleri ile geliştirilmiş, modüler yapı        ║
║       Sınıflar: Musteri | Satis | DestekTalebi               ║
╚══════════════════════════════════════════════════════════════╝
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Any
import json
import os
from pydantic import BaseModel, Field, ConfigDict, ValidationError, field_validator


# ==================== ENUMS ====================

class SatisDurumu(Enum):
    """Satış durumlarını standart şekilde tutar"""
    TAMAMLANDI = "Tamamlandı"
    BEKLEMEDE = "Beklemede"
    IPTAL = "İptal Edildi"


class TalepDurumu(Enum):
    """Destek talebi durumlarını tutar"""
    ACIK = "Açık"
    ISLEMDE = "İşlemde"
    COZULDU = "Çözüldü"
    KAPANDI = "Kapandı"


# ==================== MODEL SINIFLAR ====================

class Musteri(BaseModel):
    """
    Müşteri bilgilerini ve ilişkili kayıtları yöneten sınıf.

    Özellikler:
        musteri_id : Benzersiz müşteri kimliği
        ad         : Ad soyad veya firma adı
        telefon    : Telefon numarası
        email      : E-posta adresi
        adres      : Fiziksel adres
        _satislar  : Müşterinin satış geçmişi
        _talepler  : Müşterinin destek talepleri
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    musteri_id: str = Field(..., min_length=1)
    ad: str = Field(..., min_length=2)
    telefon: str = ""
    email: str = ""
    adres: str = ""
    kayit_tarihi: datetime = Field(default_factory=datetime.now)

    # Private attributes for relationship management
    _satislar: List[Any] = []
    _talepler: List[Any] = []

    def __init__(self, musteri_id: str, ad: str, telefon: str = "", email: str = "", adres: str = "", **kwargs):
        super().__init__(musteri_id=musteri_id, ad=ad, telefon=telefon, email=email, adres=adres, **kwargs)
        object.__setattr__(self, "_satislar", [])
        object.__setattr__(self, "_talepler", [])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        if v and "@" not in v:
            raise ValueError("Geçersiz e-posta formatı")
        return v

    def get_musteri_id(self) -> str: return self.musteri_id
    def get_ad(self) -> str: return self.ad
    def get_telefon(self) -> str: return self.telefon
    def get_email(self) -> str: return self.email
    def get_adres(self) -> str: return self.adres
    def get_kayit_tarihi(self) -> datetime: return self.kayit_tarihi

    def satis_ekle(self, satis) -> None:
        self._satislar.append(satis)

    def talep_ekle(self, talep) -> None:
        self._talepler.append(talep)

    def satis_gecmisi(self) -> list:
        return list(self._satislar)

    def aktif_satislar(self) -> list:
        return [s for s in self._satislar if s.get_durum() != SatisDurumu.IPTAL]

    def toplam_harcama(self) -> float:
        return sum(s.get_fiyat() for s in self._satislar
                   if s.get_durum() == SatisDurumu.TAMAMLANDI)

    def acik_talep_sayisi(self) -> int:
        return len([t for t in self._talepler
                    if t.get_durum() in (TalepDurumu.ACIK, TalepDurumu.ISLEMDE)])

    def to_dict(self) -> dict:
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: dict):
        m = cls(
            data["musteri_id"],
            data["ad"],
            data.get("telefon", ""),
            data.get("email", ""),
            data.get("adres", "")
        )
        m.kayit_tarihi = datetime.fromisoformat(
            data.get("kayit_tarihi", datetime.now().isoformat()))
        return m

    def __repr__(self) -> str:
        return f"Musteri({self.musteri_id}, {self.ad})"


class Satis(BaseModel):
    """
    Satış kayıtlarını ve durumlarını yöneten sınıf.

    Özellikler:
        satis_id     : Benzersiz satış kimliği
        musteri      : İlgili Musteri nesnesi
        urun         : Satılan ürün/hizmet adı
        fiyat        : Satış tutarı
        durum        : Satış durumu
        tarih        : Satış tarihi
        aciklama     : Ek notlar
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    satis_id: int
    musteri: Any
    urun: str = Field(..., min_length=1)
    fiyat: float = Field(..., gt=0)
    durum: SatisDurumu = SatisDurumu.TAMAMLANDI
    tarih: datetime = Field(default_factory=datetime.now)
    aciklama: str = ""

    def __init__(self, satis_id: int, musteri: Any, urun: str, fiyat: float, aciklama: str = "", **kwargs):
        super().__init__(satis_id=satis_id, musteri=musteri, urun=urun, fiyat=fiyat, aciklama=aciklama, **kwargs)

    def get_satis_id(self) -> int: return self.satis_id
    def get_musteri(self) -> Any: return self.musteri
    def get_urun(self) -> str: return self.urun
    def get_fiyat(self) -> float: return self.fiyat
    def get_durum(self) -> SatisDurumu: return self.durum
    def get_tarih(self) -> datetime: return self.tarih
    def get_aciklama(self) -> str: return self.aciklama

    def durum_guncelle(self, yeni_durum: SatisDurumu) -> tuple[bool, str]:
        eski = self.durum.value
        self.durum = yeni_durum
        return True, f"Satış #{self.satis_id}: {eski} → {yeni_durum.value}"

    def satis_bilgisi(self) -> dict:
        return {
            "satis_id": self.satis_id,
            "musteri_id": self.musteri.get_musteri_id(),
            "musteri": self.musteri.get_ad(),
            "urun": self.urun,
            "fiyat": f"₺{self.fiyat:,.2f}",
            "durum": self.durum.value,
            "tarih": self.tarih.strftime("%d.%m.%Y %H:%M"),
            "aciklama": self.aciklama or "—"
        }

    def to_dict(self) -> dict:
        data = self.model_dump(mode='json')
        data["musteri_id"] = self.musteri.get_musteri_id()
        del data["musteri"]
        return data

    @classmethod
    def from_dict(cls, data: dict, musteri: Musteri):
        s = cls(
            data["satis_id"],
            musteri,
            data["urun"],
            data["fiyat"],
            data.get("aciklama", "")
        )
        s.durum = SatisDurumu[data.get("durum", "TAMAMLANDI")]
        s.tarih = datetime.fromisoformat(data.get("tarih", datetime.now().isoformat()))
        return s

    def __repr__(self) -> str:
        return f"Satis(#{self.satis_id}, {self.musteri.get_ad()}, ₺{self.fiyat:.2f})"


class DestekTalebi(BaseModel):
    """
    Müşteri destek taleplerini yöneten sınıf.

    Özellikler:
        talep_id     : Benzersiz talep kimliği
        musteri      : İlgili Musteri nesnesi
        konu         : Talep konusu
        aciklama     : Detaylı açıklama
        durum        : Talep durumu
        olusturma    : Talep oluşturulma tarihi
        kapanma      : Talep kapanma tarihi
        cozum_notu   : Çözüm açıklaması
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    talep_id: int
    musteri: Any
    konu: str = Field(..., min_length=2)
    aciklama: str = ""
    durum: TalepDurumu = TalepDurumu.ACIK
    olusturma: datetime = Field(default_factory=datetime.now)
    kapanma: Optional[datetime] = None
    cozum_notu: str = ""

    def __init__(self, talep_id: int, musteri: Any, konu: str, aciklama: str = "", **kwargs):
        super().__init__(talep_id=talep_id, musteri=musteri, konu=konu, aciklama=aciklama, **kwargs)

    def get_talep_id(self) -> int: return self.talep_id
    def get_musteri(self) -> Any: return self.musteri
    def get_konu(self) -> str: return self.konu
    def get_aciklama(self) -> str: return self.aciklama
    def get_durum(self) -> TalepDurumu: return self.durum
    def get_olusturma(self) -> datetime: return self.olusturma
    def get_kapanma(self) -> Optional[datetime]: return self.kapanma
    def get_cozum_notu(self) -> str: return self.cozum_notu

    def durum_guncelle(self, yeni_durum: TalepDurumu, cozum_notu: str = "") -> tuple[bool, str]:
        eski = self.durum.value
        self.durum = yeni_durum
        if yeni_durum in (TalepDurumu.COZULDU, TalepDurumu.KAPANDI):
            self.kapanma = datetime.now()
            if cozum_notu:
                self.cozum_notu = cozum_notu
        return True, f"Talep #{self.talep_id}: {eski} → {yeni_durum.value}"

    def cozum_suresi(self) -> Optional[int]:
        if self.kapanma:
            return int((self.kapanma - self.olusturma).total_seconds() / 3600)
        return None

    def talep_bilgisi(self) -> dict:
        sure = self.cozum_suresi()
        return {
            "talep_id": self.talep_id,
            "musteri_id": self.musteri.get_musteri_id(),
            "musteri": self.musteri.get_ad(),
            "konu": self.konu,
            "durum": self.durum.value,
            "olusturma": self.olusturma.strftime("%d.%m.%Y %H:%M"),
            "kapanma": self.kapanma.strftime("%d.%m.%Y %H:%M") if self.kapanma else "—",
            "cozum_suresi": f"{sure} saat" if sure else "Devam ediyor",
            "cozum_notu": self.cozum_notu or "—"
        }

    def to_dict(self) -> dict:
        data = self.model_dump(mode='json')
        data["musteri_id"] = self.musteri.get_musteri_id()
        del data["musteri"]
        return data

    @classmethod
    def from_dict(cls, data: dict, musteri: Musteri):
        t = cls(
            data["talep_id"],
            musteri,
            data["konu"],
            data.get("aciklama", "")
        )
        t.durum = TalepDurumu[data.get("durum", "ACIK")]
        t.olusturma = datetime.fromisoformat(data.get("olusturma", datetime.now().isoformat()))
        if data.get("kapanma"):
            t.kapanma = datetime.fromisoformat(data["kapanma"])
        t.cozum_notu = data.get("cozum_notu", "")
        return t

    def __repr__(self) -> str:
        return f"DestekTalebi(#{self.talep_id}, {self.musteri.get_ad()}, {self.durum.value})"


# ==================== RAPORLAMA ====================

class Rapor:
    def __init__(self, sistem):
        self._sistem = sistem

    def satis_raporu(self, musteri_id: str = None) -> dict:
        satislar = [s for s in self._sistem.get_tum_satislar()
                    if s.get_durum() == SatisDurumu.TAMAMLANDI]
        if musteri_id:
            satislar = [s for s in satislar
                        if s.get_musteri().get_musteri_id() == musteri_id]
        toplam_gelir = sum(s.get_fiyat() for s in satislar)
        ort_fiyat = toplam_gelir / len(satislar) if satislar else 0
        return {
            "toplam_satis": len(satislar),
            "toplam_gelir": f"₺{toplam_gelir:,.2f}",
            "ortalama_fiyat": f"₺{ort_fiyat:,.2f}",
            "bekleyen_satis": len([s for s in self._sistem.get_tum_satislar()
                                     if s.get_durum() == SatisDurumu.BEKLEMEDE]),
            "iptal_satis": len([s for s in self._sistem.get_tum_satislar()
                                if s.get_durum() == SatisDurumu.IPTAL])
        }

    def musteri_raporu(self) -> list[dict]:
        rapor = []
        for musteri in self._sistem.get_musteriler().values():
            satislar = musteri.satis_gecmisi()
            tamamlanan = [s for s in satislar if s.get_durum() == SatisDurumu.TAMAMLANDI]
            rapor.append({
                "musteri_id": musteri.get_musteri_id(),
                "ad": musteri.get_ad(),
                "toplam_satis": len(tamamlanan),
                "toplam_harcama": f"₺{musteri.toplam_harcama():,.2f}",
                "acik_talep": musteri.acik_talep_sayisi(),
                "telefon": musteri.get_telefon(),
                "email": musteri.get_email()
            })
        return rapor

    def destek_raporu(self) -> dict:
        talepler = self._sistem.get_tum_talepler()
        durumlar = {}
        for t in talepler:
            d = t.get_durum().value
            durumlar[d] = durumlar.get(d, 0) + 1
        cozulen = [t for t in talepler if t.get_durum() == TalepDurumu.COZULDU]
        ort_sure = sum(t.cozum_suresi() or 0 for t in cozulen) / max(len(cozulen), 1)
        return {
            "toplam_talep": len(talepler),
            "acik_talep": durumlar.get("Açık", 0),
            "islemede_talep": durumlar.get("İşlemde", 0),
            "cozuldu_talep": durumlar.get("Çözüldü", 0),
            "kapandi_talep": durumlar.get("Kapandı", 0),
            "ortalama_cozum": f"{ort_sure:.1f} saat"
        }

    def sistem_ozeti(self) -> dict:
        s = self._sistem
        satislar = s.get_tum_satislar()
        tamamlanan = [x for x in satislar if x.get_durum() == SatisDurumu.TAMAMLANDI]
        toplam_gelir = sum(x.get_fiyat() for x in tamamlanan)
        return {
            "toplam_musteri": len(s.get_musteriler()),
            "toplam_satis": len(satislar),
            "tamamlanan_satis": len(tamamlanan),
            "toplam_gelir": f"₺{toplam_gelir:,.2f}",
            "toplam_talep": len(s.get_tum_talepler()),
            "acik_talep": len([t for t in s.get_tum_talepler()
                               if t.get_durum() in (TalepDurumu.ACIK, TalepDurumu.ISLEMDE)])
        }


# ==================== ANA SİSTEM ====================

class CRMSistemi:
    def __init__(self):
        self._musteriler: dict[str, Musteri] = {}
        self._satislar: list[Satis] = []
        self._talepler: list[DestekTalebi] = []
        self._sonraki_sid: int = 1
        self._sonraki_tid: int = 1

    def verileri_kaydet(self, dosya_adi: str = "crm_data.json") -> bool:
        try:
            data = {
                "musteriler": [m.to_dict() for m in self._musteriler.values()],
                "satislar": [s.to_dict() for s in self._satislar],
                "talepler": [t.to_dict() for t in self._talepler],
                "counters": {"sid": self._sonraki_sid, "tid": self._sonraki_tid}
            }
            with open(dosya_adi, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False

    def verileri_yukle(self, dosya_adi: str = "crm_data.json") -> bool:
        if not os.path.exists(dosya_adi):
            return False
        try:
            with open(dosya_adi, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._musteriler.clear()
            for d in data.get("musteriler", []):
                m = Musteri.from_dict(d)
                self._musteriler[m.get_musteri_id()] = m
            self._satislar.clear()
            for d in data.get("satislar", []):
                musteri = self._musteriler.get(d["musteri_id"])
                if musteri:
                    s = Satis.from_dict(d, musteri)
                    self._satislar.append(s)
                    musteri.satis_ekle(s)
            self._talepler.clear()
            for d in data.get("talepler", []):
                musteri = self._musteriler.get(d["musteri_id"])
                if musteri:
                    t = DestekTalebi.from_dict(d, musteri)
                    self._talepler.append(t)
                    musteri.talep_ekle(t)
            self._sonraki_sid = data.get("counters", {}).get("sid", 1)
            self._sonraki_tid = data.get("counters", {}).get("tid", 1)
            return True
        except Exception:
            return False

    def musteri_ekle(self, musteri: Musteri) -> tuple[bool, str]:
        if musteri.get_musteri_id() in self._musteriler:
            return False, f"ID '{musteri.get_musteri_id()}' zaten kayıtlı."
        for m in self._musteriler.values():
            if m.get_email() and m.get_email() == musteri.get_email():
                return False, "Bu e-posta adresi zaten kayıtlı."
        self._musteriler[musteri.get_musteri_id()] = musteri
        return True, f"✓ '{musteri.get_ad()}' müşteri olarak kaydedildi."

    def musteri_sil(self, musteri_id: str) -> tuple[bool, str]:
        if musteri_id not in self._musteriler:
            return False, "Müşteri bulunamadı."
        m = self._musteriler[musteri_id]
        aktif_satis = [s for s in m.satis_gecmisi()
                       if s.get_durum() in (SatisDurumu.TAMAMLANDI, SatisDurumu.BEKLEMEDE)]
        if aktif_satis:
            return False, f"'{m.get_ad()}' adlı müşterinin {len(aktif_satis)} aktif satış kaydı var."
        if m.acik_talep_sayisi() > 0:
            return False, f"'{m.get_ad()}' adlı müşterinin açık destek talebi var."
        ad = m.get_ad()
        del self._musteriler[musteri_id]
        return True, f"✓ '{ad}' sistemden silindi."

    def get_musteriler(self) -> dict[str, Musteri]:
        return self._musteriler.copy()

    def musteri_bul(self, musteri_id: str) -> Optional[Musteri]:
        return self._musteriler.get(musteri_id)

    def satis_ekle(self, musteri_id: str, urun: str, fiyat: float,
                   aciklama: str = "") -> tuple[bool, str]:
        if musteri_id not in self._musteriler:
            return False, "Müşteri bulunamadı."
        musteri = self._musteriler[musteri_id]
        try:
            satis = Satis(self._sonraki_sid, musteri, urun, fiyat, aciklama)
        except ValidationError as e:
            return False, f"Veri hatası: {e.errors()[0].get('msg')}"
            
        self._sonraki_sid += 1
        self._satislar.append(satis)
        musteri.satis_ekle(satis)
        return True, (
            f"✅ Satış kaydedildi!\n"
            f"   Satış No : #{satis.get_satis_id()}\n"
            f"   Müşteri  : {musteri.get_ad()}\n"
            f"   Ürün     : {urun}\n"
            f"   Fiyat    : ₺{fiyat:,.2f}\n"
            f"   Tarih    : {satis.get_tarih().strftime('%d.%m.%Y %H:%M')}"
        )

    def satis_durum_guncelle(self, satis_id: int,
                             yeni_durum: SatisDurumu) -> tuple[bool, str]:
        satis = next((s for s in self._satislar if s.get_satis_id() == satis_id), None)
        if not satis:
            return False, "Satış bulunamadı."
        return satis.durum_guncelle(yeni_durum)

    def get_tum_satislar(self) -> list[Satis]:
        return list(self._satislar)

    def get_musteri_satislar(self, musteri_id: str) -> list[Satis]:
        musteri = self._musteriler.get(musteri_id)
        if musteri:
            return musteri.satis_gecmisi()
        return []

    def talep_olustur(self, musteri_id: str, konu: str,
                       aciklama: str = "") -> tuple[bool, str]:
        if musteri_id not in self._musteriler:
            return False, "Müşteri bulunamadı."
        musteri = self._musteriler[musteri_id]
        try:
            talep = DestekTalebi(self._sonraki_tid, musteri, konu, aciklama)
        except ValidationError as e:
            return False, f"Veri hatası: {e.errors()[0].get('msg')}"
            
        self._sonraki_tid += 1
        self._talepler.append(talep)
        musteri.talep_ekle(talep)
        return True, (
            f"✅ Destek talebi oluşturuldu!\n"
            f"   Talep No : #{talep.get_talep_id()}\n"
            f"   Müşteri  : {musteri.get_ad()}\n"
            f"   Konu     : {konu}\n"
            f"   Durum    : {talep.get_durum().value}"
        )

    def talep_durum_guncelle(self, talep_id: int, yeni_durum: TalepDurumu,
                             cozum_notu: str = "") -> tuple[bool, str]:
        talep = next((t for t in self._talepler if t.get_talep_id() == talep_id), None)
        if not talep:
            return False, "Talep bulunamadı."
        return talep.durum_guncelle(yeni_durum, cozum_notu)

    def get_tum_talepler(self) -> list[DestekTalebi]:
        return list(self._talepler)

    def get_acik_talepler(self) -> list[DestekTalebi]:
        return [t for t in self._talepler
                if t.get_durum() in (TalepDurumu.ACIK, TalepDurumu.ISLEMDE)]

    def rapor_olustur(self) -> Rapor:
        return Rapor(self)

    def detayli_rapor(self) -> dict:
        return self.rapor_olustur().sistem_ozeti()

    def __repr__(self) -> str:
        return (f"CRMSistemi("
                f"musteri:{len(self._musteriler)}, "
                f"satis:{len(self._satislar)}, "
                f"talep:{len(self._talepler)})")


# ==================== KONSOL MENÜSÜ ====================

def yazdir_baslik(baslik: str) -> None:
    print("\n" + "═" * 60)
    print(f"   🏢  {baslik}")
    print("═" * 60)

def yazdir_ayrac() -> None:
    print("─" * 60)

def ana_menu() -> None:
    print("\n" + "═" * 60)
    print("           🏢  BASİT CRM SİSTEMİ")
    print("═" * 60)
    print("  ── Müşteri İşlemleri ────────────────────────────")
    print("  1  ➜  Yeni müşteri ekle")
    print("  2  ➜  Tüm müşterileri listele")
    print("  3  ➜  Müşteri sil")
    print("  ── Satış İşlemleri ─────────────────────────────")
    print("  4  ➜  Satış kaydı ekle")
    print("  5  ➜  Satış durumu güncelle")
    print("  6  ➜  Tüm satışları listele")
    print("  ── Destek Talepleri ────────────────────────────")
    print("  7  ➜  Yeni destek talebi oluştur")
    print("  8  ➜  Talep durumu güncelle")
    print("  9  ➜  Tüm talepleri listele")
    print("  ── Raporlar ────────────────────────────────────")
    print("  10 ➜  Sistem özeti")
    print("  11 ➜  Müşteri raporu")
    print("  12 ➜  Satış raporu")
    print("  13 ➜  Destek raporu")
    print("  ── Genel ───────────────────────────────────────")
    print("  14 ➜  Verileri kaydet")
    print("  15 ➜  Verileri yükle")
    print("   0 ➜  Çıkış")
    print("═" * 60)


def musteri_ekle_menu(sistem: CRMSistemi):
    yazdir_baslik("Yeni Müşteri Ekle")
    mid = input("  Müşteri ID (örn. M001) : ").strip()
    ad = input("  Ad Soyad / Firma        : ").strip()
    tel = input("  Telefon                 : ").strip()
    email = input("  E-posta                 : ").strip()
    adres = input("  Adres (opsiyonel)       : ").strip()
    if not mid or not ad:
        print("  [!] ID ve ad zorunludur.")
        return
    try:
        m = Musteri(mid, ad, tel, email, adres)
    except ValidationError as e:
        print(f"  ❌ Doğrulama hatası: {e.errors()[0].get('msg')}")
        return
        
    ok, msg = sistem.musteri_ekle(m)
    print(f"\n  {'✅' if ok else '❌'} {msg}")


def musterileri_listele(sistem: CRMSistemi):
    yazdir_baslik("Müşteri Listesi")
    musteriler = sistem.get_musteriler()
    if not musteriler:
        print("  Henüz müşteri eklenmedi.")
        return
    print(f"\n  {'ID':<8} {'AD SOYAD':<25} {'TELEFON':<16} {'E-POSTA':<28} {'HARCAMA':<12}")
    yazdir_ayrac()
    for m in musteriler.values():
        harcama = m.toplam_harcama()
        print(f"  {m.get_musteri_id():<8} {m.get_ad():<25} "
              f"{m.get_telefon() or '—':<16} {m.get_email() or '—':<28} "
              f"₺{harcama:>10,.2f}")


def musteri_sil_menu(sistem: CRMSistemi):
    yazdir_baslik("Müşteri Sil")
    mid = input("  Silinecek Müşteri ID: ").strip()
    ok, msg = sistem.musteri_sil(mid)
    print(f"\n  {'✅' if ok else '❌'} {msg}")


def satis_ekle_menu(sistem: CRMSistemi):
    yazdir_baslik("Satış Kaydı Ekle")
    musteriler = sistem.get_musteriler()
    if not musteriler:
        print("  Önce müşteri eklemelisiniz.")
        return
    print("  Müşteriler:")
    for m in musteriler.values():
        print(f"    [{m.get_musteri_id()}] {m.get_ad()}")
    mid = input("\n  Müşteri ID : ").strip()
    urun = input("  Ürün/Hizmet: ").strip()
    try:
        fiyat = float(input("  Fiyat ₺    : ").strip())
    except ValueError:
        print("  [!] Geçersiz fiyat.")
        return
    aciklama = input("  Açıklama (opsiyonel): ").strip()
    ok, msg = sistem.satis_ekle(mid, urun, fiyat, aciklama)
    print(f"\n  {'✅' if ok else '❌'}")
    print(msg)


def satis_durum_menu(sistem: CRMSistemi):
    yazdir_baslik("Satış Durumu Güncelle")
    satislar = sistem.get_tum_satislar()
    if not satislar:
        print("  Henüz satış kaydı yok.")
        return
    print("  Satışlar:")
    for s in satislar:
        durum_emoji = {"Tamamlandı": "✅", "Beklemede": "⏳", "İptal Edildi": "❌"}
        emoji = durum_emoji.get(s.get_durum().value, "•")
        print(f"    #{s.get_satis_id():>3} | {emoji} {s.get_durum().value:<14} | "
              f"{s.get_musteri().get_ad():<20} | {s.get_urun():<20} | ₺{s.get_fiyat():,.2f}")
    try:
        sid = int(input("\n  Satış ID: ").strip())
    except ValueError:
        print("  [!] Geçersiz ID.")
        return
    print("\n  Yeni Durum:")
    for i, d in enumerate(SatisDurumu, 1):
        print(f"    {i}. {d.value}")
    try:
        secim = int(input("  Seçiminiz: ").strip()) - 1
        yeni_durum = list(SatisDurumu)[secim]
    except (ValueError, IndexError):
        print("  [!] Geçersiz seçim.")
        return
    ok, msg = sistem.satis_durum_guncelle(sid, yeni_durum)
    print(f"\n  {'✅' if ok else '❌'} {msg}")


def satislari_listele(sistem: CRMSistemi):
    yazdir_baslik("Tüm Satışlar")
    satislar = sistem.get_tum_satislar()
    if not satislar:
        print("  Henüz satış kaydı yok.")
        return
    print(f"\n  {'ID':>4}  {'MÜŞTERİ':<22} {'ÜRÜN':<22} {'FİYAT':>10}  {'DURUM':<14}  {'TARİH':<16}")
    yazdir_ayrac()
    for s in satislar:
        durum_emoji = {"Tamamlandı": "✅", "Beklemede": "⏳", "İptal Edildi": "❌"}
        emoji = durum_emoji.get(s.get_durum().value, "•")
        print(f"  #{s.get_satis_id():>3}  {s.get_musteri().get_ad():<22} "
              f"{s.get_urun():<22} ₺{s.get_fiyat():>9,.2f}  "
              f"{emoji} {s.get_durum().value:<12}  "
              f"{s.get_tarih().strftime('%d.%m.%Y %H:%M')}")


def talep_olustur_menu(sistem: CRMSistemi):
    yazdir_baslik("Yeni Destek Talebi")
    musteriler = sistem.get_musteriler()
    if not musteriler:
        print("  Önce müşteri eklemelisiniz.")
        return
    print("  Müşteriler:")
    for m in musteriler.values():
        print(f"    [{m.get_musteri_id()}] {m.get_ad()}")
    mid = input("\n  Müşteri ID: ").strip()
    konu = input("  Konu      : ").strip()
    aciklama = input("  Açıklama  : ").strip()
    if not konu:
        print("  [!] Konu zorunludur.")
        return
    ok, msg = sistem.talep_olustur(mid, konu, aciklama)
    print(f"\n  {'✅' if ok else '❌'}")
    print(msg)


def talep_durum_menu(sistem: CRMSistemi):
    yazdir_baslik("Talep Durumu Güncelle")
    talepler = sistem.get_tum_talepler()
    if not talepler:
        print("  Henüz destek talebi yok.")
        return
    print("  Talepler:")
    for t in talepler:
        durum_renk = {"Açık": "🔴", "İşlemde": "🟡", "Çözüldü": "🟢", "Kapandı": "⚫"}
        emoji = durum_renk.get(t.get_durum().value, "•")
        print(f"    #{t.get_talep_id():>3} | {emoji} {t.get_durum().value:<10} | "
              f"{t.get_musteri().get_ad():<20} | {t.get_konu()[:30]}")
    try:
        tid = int(input("\n  Talep ID: ").strip())
    except ValueError:
        print("  [!] Geçersiz ID.")
        return
    print("\n  Yeni Durum:")
    for i, d in enumerate(TalepDurumu, 1):
        print(f"    {i}. {d.value}")
    try:
        secim = int(input("  Seçiminiz: ").strip()) - 1
        yeni_durum = list(TalepDurumu)[secim]
    except (ValueError, IndexError):
        print("  [!] Geçersiz seçim.")
        return
    cozum = ""
    if yeni_durum in (TalepDurumu.COZULDU, TalepDurumu.KAPANDI):
        cozum = input("  Çözüm notu: ").strip()
    ok, msg = sistem.talep_durum_guncelle(tid, yeni_durum, cozum)
    print(f"\n  {'✅' if ok else '❌'} {msg}")


def talepleri_listele(sistem: CRMSistemi):
    yazdir_baslik("Tüm Destek Talepleri")
    talepler = sistem.get_tum_talepler()
    if not talepler:
        print("  Henüz destek talebi yok.")
        return
    print(f"\n  {'ID':>4}  {'MÜŞTERİ':<20} {'KONU':<28} {'DURUM':<12}  {'OLUŞTURMA':<16}")
    yazdir_ayrac()
    for t in talepler:
        durum_renk = {"Açık": "🔴", "İşlemde": "🟡", "Çözüldü": "🟢", "Kapandı": "⚫"}
        emoji = durum_renk.get(t.get_durum().value, "•")
        print(f"  #{t.get_talep_id():>3}  {t.get_musteri().get_ad():<20} "
              f"{t.get_konu()[:28]:<28} {emoji} {t.get_durum().value:<10}  "
              f"{t.get_olusturma().strftime('%d.%m.%Y %H:%M')}")


def sistem_ozeti(sistem: CRMSistemi):
    yazdir_baslik("Sistem Özeti")
    for k, v in sistem.detayli_rapor().items():
        print(f"  • {k:<25}: {v}")


def musteri_raporu(sistem: CRMSistemi):
    yazdir_baslik("Müşteri Raporu")
    rapor = sistem.rapor_olustur().musteri_raporu()
    if not rapor:
        print("  Müşteri bulunamadı.")
        return
    print(f"\n  {'ID':<8} {'AD SOYAD':<22} {'SATIŞ':>6} {'HARCAMA':>12} {'AÇIK TALEP':>10}")
    yazdir_ayrac()
    for r in rapor:
        print(f"  {r['musteri_id']:<8} {r['ad']:<22} {r['toplam_satis']:>6} "
              f"{r['toplam_harcama']:>12} {r['acik_talep']:>10}")


def satis_raporu(sistem: CRMSistemi):
    yazdir_baslik("Satış Raporu")
    rapor = sistem.rapor_olustur().satis_raporu()
    for k, v in rapor.items():
        print(f"  • {k:<25}: {v}")


def destek_raporu(sistem: CRMSistemi):
    yazdir_baslik("Destek Raporu")
    rapor = sistem.rapor_olustur().destek_raporu()
    for k, v in rapor.items():
        print(f"  • {k:<25}: {v}")


# ==================== ANA DÖNGÜ ====================

def main():
    print("\n" + "═" * 60)
    print("     🏢  Basit CRM Sistemi — Hoş Geldiniz!")
    print("═" * 60)

    sistem = CRMSistemi()
    sistem.verileri_yukle()

    if not sistem.get_musteriler():
        m1 = Musteri("M001", "Ahmet Yılmaz", "05551234567", "ahmet@firma.com", "İstanbul")
        m2 = Musteri("M002", "Ayşe Demir", "05559876543", "ayse@sirket.com", "Ankara")
        m3 = Musteri("M003", "Mehmet Kaya", "05553334455", "mehmet@mail.com", "İzmir")
        for m in [m1, m2, m3]:
            sistem.musteri_ekle(m)

        sistem.satis_ekle("M001", "Web Sitesi Tasarımı", 15000.0, "Kurumsal web sitesi")
        sistem.satis_ekle("M002", "SEO Danışmanlığı", 8000.0, "3 aylık paket")
        sistem.satis_ekle("M003", "Mobil Uygulama", 45000.0, "iOS & Android")

        sistem.talep_olustur("M001", "Web sitesi yavaşlık sorunu", "Ana sayfa açılış süresi çok uzun")
        sistem.talep_olustur("M002", "Raporlama hatası", "Aylık rapor PDF olarak indirilemiyor")

        print("  ✅ Demo verisi yüklendi.\n")

    MENU = {
        "1": musteri_ekle_menu,
        "2": musterileri_listele,
        "3": musteri_sil_menu,
        "4": satis_ekle_menu,
        "5": satis_durum_menu,
        "6": satislari_listele,
        "7": talep_olustur_menu,
        "8": talep_durum_menu,
        "9": talepleri_listele,
        "10": sistem_ozeti,
        "11": musteri_raporu,
        "12": satis_raporu,
        "13": destek_raporu,
    }

    while True:
        ana_menu()
        secim = input("\n  Seçiminiz: ").strip()

        if secim == "0":
            kaydet = input("\n  Çıkmadan önce kaydet? (e/h): ").strip().lower()
            if kaydet == "e":
                ok = sistem.verileri_kaydet()
                print("  ✅ Kaydedildi." if ok else "  ❌ Kayıt hatası.")
            print("\n  İyi günler! 🏢\n")
            break
        elif secim == "14":
            ok = sistem.verileri_kaydet()
            print(f"\n  {'✅ Veriler kaydedildi.' if ok else '❌ Kayıt başarısız.'}")
        elif secim == "15":
            ok = sistem.verileri_yukle()
            print(f"\n  {'✅ Veriler yüklendi.' if ok else '❌ Dosya bulunamadı.'}")
        elif secim in MENU:
            MENU[secim](sistem)
        else:
            print("  [!] Geçersiz seçim. 0-15 arası bir sayı girin.")

        input("\n  ↩  Devam etmek için Enter'a basın...")


if __name__ == "__main__":
    main()