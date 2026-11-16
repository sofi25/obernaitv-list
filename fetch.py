import urllib.request
import json
from datetime import datetime, timedelta, timezone

today = datetime.now(timezone.utc)
end_day = today + timedelta(days=3)
date_range = f"{today.strftime('%Y%m%d')}-{end_day.strftime('%Y%m%d')}"

leagues = [
    ("uefa.nations", "UEFA Nations League", "BEIN"),
    ("caf.nations", "AFCON Qualifiers", "BEIN"),
    ("fifa.worldq.conmebol", "World Cup Qualifiers", "SSC"),
    ("fifa.worldq.afc", "World Cup Qualifiers AFC", "BEIN"),
    ("fifa.friendly", "International Friendlies", "BEIN"),
    ("uefa.champions", "UEFA Champions League", "BEIN"),
    ("eng.1", "Premier League", "BEIN"),
    ("esp.1", "La Liga", "BEIN"),
    ("ita.1", "Serie A", "AD SPORTS"),
    ("fra.1", "Ligue 1", "BEIN"),
    ("ksa.1", "Saudi Pro League", "SSC")
]

matches = []

for code, name, channel in leagues:
    url = f"https://espn.com{code}/scoreboard?dates={date_range}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for ev in data.get("events", list()):
                comps = ev.get("competitions", list())
                comp = next(iter(comps), None)
                if not comp:
                    continue
                status_type = comp.get("status", dict()).get("type", dict())
                state = status_type.get("state", "pre")
                status = "LIVE" if state == "in" else ("FINISHED" if state == "post" else "UPCOMING")
                
                date_str = ev.get("date", "")
                time_hm = date_str[11:16] if len(date_str) >= 16 else "00:00"
                
                teams = comp.get("competitors", list())
                if len(teams) < 2:
                    continue
                t_first = next(iter(teams))
                home = next((c for c in teams if c.get("homeAway") == "home"), t_first)
                away = next((c for c in teams if c.get("homeAway") == "away"), t_first)
                
                h_score = home.get("score", "0")
                a_score = away.get("score", "0")
                score = time_hm if state == "pre" else f"{h_score} - {a_score}"
                
                matches.append({
                    "league": name,
                    "homeTeam": home.get("team", dict()).get("shortDisplayName", ""),
                    "homeLogo": home.get("team", dict()).get("logo", ""),
                    "awayTeam": away.get("team", dict()).get("shortDisplayName", ""),
                    "awayLogo": away.get("team", dict()).get("logo", ""),
                    "time": time_hm,
                    "status": status,
                    "score": score,
                    "channel": channel
                })
    except Exception as err:
        print("Error:", code, err)

with open("matches.json", "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print("Total saved:", len(matches))
