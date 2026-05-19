import os
import re
import requests

def clean_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()

def fetch_vavoo_channels():
    # Engellenmeyen stabil küresel Vavoo kaynak havuzu
    url = "https://githubusercontent.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    print("🔄 Canlı Vavoo global havuzundan tüm dünya kanalları indiriliyor...")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print("⚠️ Sunucu hata döndürdü, işlem güvenli modda sonlandırılıyor.")
            return

        m3u_content = response.text
        if not m3u_content or "#EXTM3U" not in m3u_content:
            print("⚠️ Veri boş veya geçersiz, işlem durduruldu.")
            return

        print("✅ Veri başarıyla indirildi. İşleme başlıyor...")
        countries_dict = {}
        output_dir = "countries"
        os.makedirs(output_dir, exist_ok=True)

        lines = m3u_content.split('\n')
        current_inf = None

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

                    # Regex ile group-title veya tvg-country etiketlerini güvenle yakalarız
                    group_match = re.search(r'group-title="([^"]+)"', current_inf, re.IGNORECASE)
                    country_match = re.search(r'tvg-country="([^"]+)"', current_inf, re.IGNORECASE)

                    if group_match:
                        country = group_match.group(1).upper().strip()
                    elif country_match:
                        country = country_match.group(1).upper().strip()

                    # Uzantı manipülasyonu
                    if ".m3u8" not in line and ".m3u" not in line:
                        line = f"{line}&ext=.m3u8" if "?" in line else f"{line}?ext=.m3u8"

                    main_file.write(f"{current_inf}\n{line}\n")

                    if country not in countries_dict:
                        countries_dict[country] = []
                    countries_dict[country].append((current_inf, line))
                    current_inf = None

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

        print("🎉 Tüm dosyalar yerel diskte başarıyla üretildi!")
    except Exception as e:
        print(f"⚠️ Beklenmeyen bir durum oluştu: {e}")

if __name__ == "__main__":
    fetch_vavoo_channels()
