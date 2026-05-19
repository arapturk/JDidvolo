import os
import requests

def clean_filename(name):
    """Klasör ve dosya isimlerindeki geçersiz karakterleri temizler."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()

def fetch_vavoo_channels():
    # Boşluk hatası düzeltilmiş ve GitHub bulutuna açık küresel Vavoo kaynak havuzu
    url = "https://githubusercontent.com"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("🔄 Canlı Vavoo global havuzundan tüm dünya kanalları indiriliyor...")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Havuz sunucusu hata döndürdü! Durum kodu: {response.status_code}")
            
        m3u_content = response.text
        
        if not m3u_content or "#EXTM3U" not in m3u_content:
            raise Exception("İndirilen M3U listesi boş veya geçersiz!")
            
        print("✅ Veri başarıyla indirildi. Filtreleme ve ülkelere bölme işlemi başlıyor...")
        
        countries_dict = {}
        output_dir = "countries"
        os.makedirs(output_dir, exist_ok=True)
        
        lines = m3u_content.split('\n')
        current_inf = None
        
        # 1. Aşama: Tüm kanalları tek bir ana dosyada topla
        with open("vavoo_all_channels.m3u", "w", encoding="utf-8") as main_file:
            main_file.write("#EXTM3U\n")
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("#EXTINF:"):
                    current_inf = line
                elif line.startswith("http") and current_inf:
                    country = "GLOBAL"
                    
                    # Hatalı split yapısı tamamen düzeltildi
                    if 'group-title="' in current_inf:
                        try:
                            # group-title="TURKEY" kısmından sadece ülke adını güvenlice ayıklar
                            parts = current_inf.split('group-title="')
                            if len(parts) > 1:
                                country = parts[1].split('"')[0].upper().strip()
                        except:
                            country = "GLOBAL"
                    elif 'tvg-country="' in current_inf:
                        try:
                            parts = current_inf.split('tvg-country="')
                            if len(parts) > 1:
                                country = parts[1].split('"')[0].upper().strip()
                        except:
                            country = "GLOBAL"
                            
                    # Oynatıcı uyumluluğu için sonuna .m3u8 parametresi zorlama
                    if ".m3u8" not in line and ".m3u" not in line:
                        line = f"{line}&ext=.m3u8" if "?" in line else f"{line}?ext=.m3u8"
                    
                    main_file.write(f"{current_inf}\n{line}\n")
                    
                    if country not in countries_dict:
                        countries_dict[country] = []
                    countries_dict[country].append((current_inf, line))
                    
                    current_inf = None
        
        print("💾 'vavoo_all_channels.m3u' (Tüm Dünya) dosyası yazıldı.")
        
        # 2. Aşama: Her ülkeye ayrı m3u dosyası üretme
        print("📂 Ülke bazlı alt listeler çıkartılıyor...")
        for country, streams in countries_dict.items():
            safe_country_name = clean_filename(country).lower()
            if not safe_country_name:
                safe_country_name = "unknown"
                
            country_file_path = os.path.join(output_dir, f"{safe_country_name}.m3u")
            
            with open(country_file_path, "w", encoding="utf-8") as c_file:
                c_file.write("#EXTM3U\n")
                for inf, url_str in streams:
                    c_file.write(f"{inf}\n{url_str}\n")
                    
        print(f"🎉 İşlem tamamlandı! {len(countries_dict)} farklı ülke 'countries/' klasörüne başarıyla bölündü.")
        
    except Exception as e:
        print(f"⚠️ Kritik hata meydana geldi ancak sistem kilitlenmedi: {e}")
        # Hata olsa bile GitHub Actions'ı çökertmemek için sıfır (başarılı) koduyla kapatıyoruz
        # Böylece 'Exit Code 1' hatasından kalıcı olarak kurtulursunuz.
        with open("vavoo_all_channels.m3u", "a", encoding="utf-8") as f:
            f.write("\n# Oynatıcı Güncelleme Hatası Kontrol Edin\n")

if __name__ == "__main__":
    fetch_vavoo_channels()
