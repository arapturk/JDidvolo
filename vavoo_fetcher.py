import json
import re
import requests

def fetch_vavoo_channels():
    # Vavoo global IPTV kanal listesi API uç noktası
    vavoo_url = "https://vavoo.to"
    # Sunucu engeline takılmamak için tarayıcı başlığı
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
        
        # API verisini işle
        channels_data = response.json()
        print(f"✅ Toplam {len(channels_data)} kanal başarıyla indirildi. M3U formatına dönüştürülüyor...")
        
        output_file = "vavoo_channels.m3u"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            for channel in channels_data:
                # Gerekli parametreleri güvenli bir şekilde al
                name = channel.get("name", "Bilinmeyen Kanal")
                url = channel.get("url")
                country = channel.get("country", "Global").upper()
                group = channel.get("group", country)
                logo = channel.get("logo", "")
                
                if not url:
                    continue
                
                # Link formatının .m3u8 / .m3u uyumlu bitmesini sağlama operasyonu
                # Eğer link parametre içeriyorsa (?token=vs), oynatıcıların algılaması için sonuna sahte bir uzantı eklenir
                if ".m3u8" not in url and ".m3u" not in url:
                    if "?" in url:
                        url = f"{url}&ext=.m3u8"
                    else:
                        url = f"{url}?ext=.m3u8"
                
                # M3U format standartlarında yazım (Ülke gruplamalı ve logolu)
                f.write(f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f"{url}\n")
                
        print(f"🎉 Başarılı! Tüm ülkelerin listesi '{output_file}' olarak kaydedildi.")
        
    except Exception as e:
        print(f"⚠️ Kritik Hata Oluştu: {e}")

if __name__ == "__main__":
    fetch_vavoo_channels()
