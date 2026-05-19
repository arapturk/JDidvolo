import os
import requests

def clean_filename(name):
    """Klasör ve dosya isimlerindeki geçersiz karakterleri temizler."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()

def fetch_vavoo_channels():
    vavoo_url = "https://vavoo.to"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    print("🔄 Vavoo global sunucusundan kanallar çekiliyor...")
    try:
        response = requests.get(vavoo_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Sunucu hatası! Kod: {response.status_code}")
            return
        
        channels_data = response.json()
        print(f"✅ Toplam {len(channels_data)} kanal indirildi. Filtreleme ve ayrıştırma başlıyor...")
        
        # Ülkelere göre gruplamak için bir sözlük oluşturuyoruz
        countries_dict = {}
        
        # Klasör yapısını hazırla
        output_dir = "countries"
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Aşama: Tüm kanalları tek bir ana dosyaya yaz ve ülkelere göre grupla
        with open("vavoo_all_channels.m3u", "w", encoding="utf-8") as main_file:
            main_file.write("#EXTM3U\n")
            
            for channel in channels_data:
                name = channel.get("name", "Bilinmeyen Kanal")
                url = channel.get("url")
                country = channel.get("country", "GLOBAL").upper().strip()
                group = channel.get("group", country)
                logo = channel.get("logo", "")
                
                if not url:
                    continue
                
                # Link sonunu .m3u8 olarak manipüle etme (IPTV oynatıcı uyumluluğu için)
                if ".m3u8" not in url and ".m3u" not in url:
                    url = f"{url}&ext=.m3u8" if "?" in url else f"{url}?ext=.m3u8"
                
                # Format satırları
                inf_line = f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}\n'
                url_line = f"{url}\n"
                
                # Ana listeye yaz
                main_file.write(inf_line)
                main_file.write(url_line)
                
                # Ülke sözlüğüne kaydet
                if country not in countries_dict:
                    countries_dict[country] = []
                countries_dict[country].append((inf_line, url_line))
        
        print("💾 'vavoo_all_channels.m3u' (Tüm Ülkeler) dosyası oluşturuldu.")
        
        # 2. Aşama: Her ülkeyi kendi dosyasına bölme
        print("📂 Ülkelere göre alt listeler oluşturuluyor...")
        for country, streams in countries_dict.items():
            safe_country_name = clean_filename(country).lower()
            if not safe_country_name:
                safe_country_name = "unknown"
                
            country_file_path = os.path.join(output_dir, f"{safe_country_name}.m3u")
            
            with open(country_file_path, "w", encoding="utf-8") as c_file:
                c_file.write("#EXTM3U\n")
                for inf_line, url_line in streams:
                    c_file.write(inf_line)
                    c_file.write(url_line)
                    
        print(f"🎉 İşlem tamamlandı! {len(countries_dict)} farklı ülke için ayrı ayrı .m3u dosyası 'countries/' klasörüne kaydedildi.")
        
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    fetch_vavoo_channels()
