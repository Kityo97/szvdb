# Politikai Hőtérkép Dashboard 🗺️

**Századvég Alapítvány – Belső elemzési eszköz**

## Telepítés és futtatás

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tartalom

| Oldal | Tartalom |
|-------|----------|
| 🏠 Főoldal | KPI-ok, OEVK térkép, navigáció |
| 🗳️ Választástörténet | 2022 egyéni + listás eredmények |
| 👥 KSH Szociológia | Demográfia, végzettség, vallás |
| 📊 Saját Kutatások | Ideológia, Big Five, médiafogyasztás |
| 🔭 Politikai Közvélemény | Pártpreferenciák, Sankey, közhangulat |
| 📱 Social Media | (hamarosan) |
| 💰 Gazdasági Adatok | Percepció, megélhetés, megtakarítás |

## Adatforrások

- **NVI 2022**: Egyéni szavazás OEVK erjkv. + Országos listás eredmény
- **KSH 2022**: Népszámlálás – Bács02 VK demográfiai adatai
- **Századvég nagykutatás**: Bács02 (N=500), Ország (N=20 014)

## Következő lépések

- Korábbi évek (2010, 2014, 2018) adatainak hozzáadása
- Interaktív choropleth térkép (GeoJSON integráció)
- Social media API integráció
- ChatGPT/Claude API összefoglaló modul
