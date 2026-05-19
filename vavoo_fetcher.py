import os
import requests

def clean_filename(name):
    """Klasör ve dosya isimlerindeki geçersiz karakterleri temizler."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()

def fetch_vavoo_channels():
    # GitHub engeline takılmayan ve Vavoo kanallarını canlı çözen küresel topluluk havuzu
    url = "https://githubusercontent.com LaneSh4rk/IPTV-Free-Links/main/vavoo.m3u"
    # Alternatif yedek havuz (Eğer ilk havuz düşerse)
    backup_url = "https://github.io"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print("🔄 Canlı Vavoo global havuzundan tüm dünya kanalları indiriliyor...")
    
    try:
        response = requests.get(url, headers=headers, timeout=25)
        if response.status_code != 200:
            print("⚠️ Ana havuz yanıt vermedi, yedek havuza geçiliyor...")
            response = requests.get(backup_url, headers=headers, timeout=25)
            
        m3u_content = response.text
        
        if not m3u_content or "#EXTM3U" not in m3u_content:
            raise Exception("Alınan M3U verisi geçersiz veya boş!")
            
        print("✅ Veri başarıyla indirildi. Tüm dünya ülkelerine göre ayrıştırma başlıyor...")
        
        countries_dict = {}
        output_dir = "countries"
        os.makedirs(output_dir, exist_ok=True)
        
        # M3U içeriğini satır satır oku
        lines = m3u_content.split('\n')
        current_inf = None
        
        # Tüm ülkeleri tek dosyada toplayacağımız ana dosya
        with open("vavoo_all_channels.m3u", "w", encoding="utf-8") as main_file:
            main_file.write("#EXTM3U\n")
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("#EXTINF:"):
                    current_inf = line
                elif line.startswith("http") and current_inf:
                    # Gelişmiş Ülke / Grup Tespiti
                    country = "GLOBAL"
                    
                    # group-title etiketinden ülkeyi yakala
                    if 'group-title="' in current_inf:
                        try:
                            country = current_inf.split('group-title="')[1].split('"')[0].upper().strip()
                        except:
                            pass
                    # Eğer group-title yoksa tvg-country etiketine bak
                    elif 'tvg-country="' in current_inf:
                        try:
                            country = current_inf.split('tvg-country="' duet)[1].split('"')[0].upper().strip()
                        except:
                            pass
                            
                    # Link sonunu oynatıcılar için .m3u8 olarak sabitle
                    if ".m3u8" not in line and ".m3u" not in line:
                        line = f"{line}&ext=.m3u8" if "?" in line else f"{line}?ext=.m3u8"
                    
                    # Ana dosyaya yaz
                    main_file.write(f"{current_inf}\n{line}\n")
                    
                    # Ülke listesi sözlüğüne ekle
                    if country not in countries_dict:
                        countries_dict[country] = []
                    countries_dict[country].append((current_inf, line))
                    
                    current_inf = None
        
        print("💾 'vavoo_all_channels.m3u' dosyası güncellendi.")
        
        # 2. Her ülkeyi kendi dosyasına bölme aşaması
        print("📂 Ülke bazlı alt klasör listeleri yazılıyor...")
        for country, streams in countries_dict.items():
            safe_country_name = clean_filename(country).lower()
            if not safe_country_name or safe_country_name == "":
                safe_country_name = "unknown"
                
            country_file_path = os.path.join(output_dir, f"{safe_country_name}.m3u")
            
            with open(country_file_path, "w", encoding="utf-8") as c_file:
                c_file.write("#EXTM3U\n")
                for inf, url_str in streams:
                    c_file.write(f"{inf}\n{url_str}\n")
                    
        print(f"🎉 Başarılı! {len(countries_dict)} adet farklı ülke listesi 'countries/' klasörüne yüklendi.")
        
    except Exception as e:
        print(f"❌ HATA: {e}")
        exit(1)

if __name__ == "__main__":
    fetch_vavoo_channels()
