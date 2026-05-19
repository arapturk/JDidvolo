import os
import requests

def clean_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()

def fetch_vavoo_channels():
    # Güncel Vavoo API uç noktası
    vavoo_url = "https://vavoo.to"
    
    # Sunucu engellerini aşmak için tarayıcı simülasyonu
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://vavoo.to",
        "Referer": "https://vavoo.to"
    }

    print("🔄 Vavoo global sunucusundan kanallar çekiliyor...")
    try:
        response = requests.get(vavoo_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            raise Exception(f"Vavoo sunucusu hata döndürdü! Durum Kodu: {response.status_code}")
            
        channels_data = response.json()
        
        # Güvenlik Kontrolü: Eğer gelen veri boşsa işlemi durdur
        if not channels_data or len(channels_data) == 0:
            raise Exception("Vavoo API başarıyla yanıt verdi ancak veri boş döndü! Sunucu engeline takılmış olabiliriz.")
            
        print(f"✅ Toplam {len(channels_data)} kanal başarıyla yakalandı! Dosyalar yazılıyor...")
        
        countries_dict = {}
        output_dir = "countries"
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Tüm kanalları tek dosyaya yaz
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
                
                # Oynatıcıların .m3u/.m3u8 sonunu görmesini sağlama
                if ".m3u8" not in url and ".m3u" not in url:
                    url = f"{url}&ext=.m3u8" if "?" in url else f"{url}?ext=.m3u8"
                
                inf_line = f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}\n'
                url_line = f"{url}\n"
                
                main_file.write(inf_line)
                main_file.write(url_line)
                
                if country not in countries_dict:
                    countries_dict[country] = []
                countries_dict[country].append((inf_line, url_line))
        
        # 2. Ülkelere göre klasörleri oluştur
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
                    
        print("🎉 Tüm dosyalar ve 'countries/' klasörü yerel diskte başarıyla oluşturuldu!")
        
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}")
        # GitHub Actions'ın hata alıp durmasını ve loglarda bunu göstermesini sağlıyoruz
        exit(1)

if __name__ == "__main__":
    fetch_vavoo_channels()
