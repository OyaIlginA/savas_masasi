import json
import os

def main():
    # Dosya isimleri
    giris_dosyasi = 'map.geojson'
    cikis_dosyasi = 'tum_ulkeler_tek_parca.geojson'

    # Dosya yollarını otomatik bul (Kodun çalıştığı klasör)
    klasor_yolu = os.path.dirname(os.path.abspath(__file__))
    giris_yolu = os.path.join(klasor_yolu, giris_dosyasi)
    cikis_yolu = os.path.join(klasor_yolu, cikis_dosyasi)

    print(f"Çalışma dizini: {klasor_yolu}")

    # Dosya kontrolü
    if not os.path.exists(giris_yolu):
        print(f"HATA: '{giris_dosyasi}' dosyası bulunamadı!")
        print("Lütfen map.geojson dosyasını bu python dosyasının yanına koyun.")
        return

    try:
        print("Dosya okunuyor...")
        with open(giris_yolu, 'r', encoding='utf-8') as f:
            data = json.load(f)

        features = data.get('features', [])
        print(f"Toplam parça sayısı: {len(features)}")

        # 1. Parçaları devletlere (state) göre grupla
        ulkeler_koordinatlari = {}
        ulke_ozellikleri = {}

        for f in features:
            props = f.get('properties', {})
            state_id = props.get('state', 0)
            
            # State ID'si 0 olanlar (genelde okyanus) hariç tutulur.
            # Hepsini istiyorsanız bu if bloğunu kaldırabilirsiniz.
            if state_id == 0:
                continue

            if state_id not in ulkeler_koordinatlari:
                ulkeler_koordinatlari[state_id] = []
                # İlk parçanın özelliklerini (isim, renk vb.) sakla
                ulke_ozellikleri[state_id] = props

            # Geometriyi al
            geom = f.get('geometry', {})
            if not geom: continue
            
            coords = geom.get('coordinates')
            g_type = geom.get('type')

            # Tüm koordinatları tek bir listede topla
            if g_type == 'Polygon':
                ulkeler_koordinatlari[state_id].append(coords)
            elif g_type == 'MultiPolygon':
                # MultiPolygon ise içindeki poligonları listeye ekle
                ulkeler_koordinatlari[state_id].extend(coords)

        print(f"Tespit edilen ülke sayısı: {len(ulkeler_koordinatlari)}")

        # 2. Yeni 'Feature'ları oluştur
        yeni_features = []
        for state_id, polygon_list in ulkeler_koordinatlari.items():
            yeni_feature = {
                "type": "Feature",
                "properties": ulke_ozellikleri[state_id],
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": polygon_list
                }
            }
            yeni_features.append(yeni_feature)

        # 3. Dosyayı kaydet
        yeni_data = {
            "type": "FeatureCollection",
            "features": yeni_features
        }

        with open(cikis_yolu, 'w', encoding='utf-8') as f:
            json.dump(yeni_data, f)

        print(f"İŞLEM BAŞARILI! Yeni dosya oluşturuldu: {cikis_dosyasi}")
        print(f"Orijinal parça sayısı: {len(features)} -> Yeni parça sayısı: {len(yeni_features)}")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    main()