import json
import os
import datetime

JSON_FILE = "saraksts.json"
TXT_FILE = "saraksts.txt"
DATE_FORMAT = "%d/%m/%Y"

class _NoColor: RESET_ALL = ''
class _F:
    GREEN = ''
    YELLOW = ''
    RED = ''
    CYAN = ''
    MAGENTA = ''
Fore = _F()
Style = _NoColor()

def load_data(): #Nolasa JSON failu, ja tas eksistē. Ja nav vai ir kļūda, atgriež tukšu sarakstu.
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def save_data(data): #Saglabā datus JSON un TXT failos.
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{Fore.RED}Kļūda saglabājot JSON: {e}{Style.RESET_ALL}")
    try:
        with open(TXT_FILE, "w", encoding="utf-8") as f:
            if not data:
                f.write("Nav ierakstu.\n")
            for entry in data:
                f.write(f"Atkritumu veids: {entry.get('waste_type')}\n")
                typ = entry.get('collection_type')
                typ_nos = {'weekly':'Ik nedēļu', 'monthly':'Ik mēnesi', 'one-time':'Vienreizējs'}.get(typ, typ)
                f.write(f"Tips: {typ_nos}\n")
                f.write(f"Nākamais izvešanas datums: {entry.get('next_date')}\n")
                f.write("-" * 30 + "\n")
    except Exception as e:
        print(f"{Fore.RED}Kļūda saglabājot TXT: {e}{Style.RESET_ALL}")

def parse_date(s): #Pārveido lietotāja ievadīto datuma tekstu par datuma objektu. Atgriež None, ja formāts nav derīgs.
    try:
        return datetime.datetime.strptime(s.strip().replace('.', '/'), DATE_FORMAT).date()
    except Exception:
        return None

def format_date(d): #Pārveido datuma objektu, par tekstu norādītajā formātā.
    return d.strftime(DATE_FORMAT)

def calculate_next_for_entry(entry, today): #Aprēķina nākamo izvešanas datumu(nedēļas vai mēneša cikls). Ja datums jau pagājis, to pārbīda uz nākamo atbilstošo periodu.
    try:
        next_d = parse_date(entry.get("next_date"))
        if not next_d:
            return entry
        typ = entry.get("collection_type")
        if typ == "weekly":
            while next_d < today:
                next_d = next_d + datetime.timedelta(days=7)
            entry["next_date"] = format_date(next_d)
        elif typ == "monthly":
            while next_d < today:
                next_d = next_d + datetime.timedelta(days=30)
            entry["next_date"] = format_date(next_d)
    except Exception:
        pass
    return entry

def check_today_reminders(data): #Pārbauda, vai šodien ir kādas atkritumu izvešanas. Izvada atgādinājumu, ja kādam ierakstam 'next_date' sakrīt ar šodienu.

    today = datetime.date.today()
    today_s = format_date(today)
    reminded = False
    for entry in data:
        if entry.get("next_date") == today_s:
            print(f"{Fore.GREEN}✅ ATGĀDINĀJUMS: Šodien jāizved '{entry.get('waste_type')}'! 🗑️{Style.RESET_ALL}")
            reminded = True
    if not reminded:
        print(f"{Fore.CYAN}ℹ️  Šodien: {today_s} — Nav plānoto izvešanu.{Style.RESET_ALL}")
    return reminded

def add_entry(data): #Pievieno jaunu izvešanas grafika ierakstu -  prasa atkritumu veidu, izvešanas tipu un datumu.

    print(f"{Fore.MAGENTA}=== Pievienot jaunu izvešanas grafiku ==={Style.RESET_ALL}")
    while True:
        waste_type = input("Atkritumu veids🌏: ").strip()
        if waste_type:
            break
        print(f"{Fore.YELLOW}⛔Ievade nedrīkst būt tukša.{Style.RESET_ALL}")
    types_map = {"1":"weekly", "2":"monthly", "3":"one-time"}
    while True:
        print("🔢Izvešanas veids: 1 = Ik nedēļu, 2 = Ik mēnesi, 3 = Vienreizējs")
        typ_choice = input("Izvēlieties tipu 1, 2 vai 3): ").strip()
        if typ_choice in types_map:
            collection_type = types_map[typ_choice]
            break
        print(f"{Fore.YELLOW}🔢Lūdzu izvēlieties 1, 2 vai 3.{Style.RESET_ALL}")
    while True:
        date_input = input(f"🔢Ievadiet datumu ({DATE_FORMAT.lower()}): ").strip()
        dt = parse_date(date_input)
        if not dt:
            print(f"{Fore.YELLOW}⛔Nederīgs datums. Lietojiet formātu {DATE_FORMAT}.{Style.RESET_ALL}")
            continue
        today = datetime.date.today()
        if dt < today:
            print(f"{Fore.YELLOW}⛔Datums nedrīkst būt pagātnē. Ievadiet nākotnes datumu.{Style.RESET_ALL}")
            continue
        break
    new_entry = {
        "waste_type": waste_type,
        "collection_type": collection_type,
        "next_date": format_date(dt)
    }
    data.append(new_entry)
    save_data(data)
    print(f"{Fore.GREEN}✅ Ieraksts pievienots: {waste_type} — {collection_type} — {format_date(dt)}{Style.RESET_ALL}")

def view_schedules(data): # Parāda visus saglabātos grafikus un piedāvā iespēju dzēst ierakstu.
    print(f"{Fore.MAGENTA}=== Aktīvie grafiki ==={Style.RESET_ALL}")
    if not data:
        print("Nav ierakstu.😕")
        return
    for i, entry in enumerate(data, 1):
        typ_nos = {'weekly':'Ik nedēļu', 'monthly':'Ik mēnesi', 'one-time':'Vienreizējs'}.get(entry.get('collection_type'), entry.get('collection_type'))
        print(f"{i}. {entry.get('waste_type')} — {typ_nos} — Nākamais: {entry.get('next_date')}")
    while True:
        print("\n1 = Dzēst ierakstu, 2 = Atgriezties galvenajā izvēlnē")
        c = input("> ").strip()
        if c == "1":
            delete_schedule(data)
            break
        elif c == "2":
            break
        else:
            print(f"{Fore.YELLOW}⛔Izvēle nederīga.{Style.RESET_ALL}")

def delete_schedule(data): #Dzēš lietotāja izvēlēto ierakstu pēc numura. Saglabā failā izmaiņas pēc dzēšanas.

    if not data:
        print("Nav ierakstu.😕")
        return
    try:
        num = int(input("🔢Ievadiet dzēšamā ieraksta numuru: ").strip())
        if 1 <= num <= len(data):
            removed = data.pop(num-1)
            save_data(data)
            print(f"{Fore.GREEN}✅ Ieraksts izdzēsts: {removed.get('waste_type')} — {removed.get('next_date')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⛔Nepareizs numurs.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.YELLOW}🔢Lūdzu ievadiet skaitli.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Kļūda dzēšot: {e}{Style.RESET_ALL}")

def update_all_dates(data): # Pārskata visus ierakstus, atjauno 'next_date' un dzēš ''vienreizējos'' ierakstus.
    today = datetime.date.today()
    changed = False
    data_to_keep = []
    original_len = len(data)

    for entry in data:
        next_d = parse_date(entry.get("next_date"))
        if entry.get("collection_type") == "one-time" and next_d and next_d < today:
            print(f"{Fore.YELLOW}ℹ️  Automātiski dzēsts pagājis vienreizējs ieraksts: {entry.get('waste_type')} ({entry.get('next_date')}){Style.RESET_ALL}")
            changed = True
            continue

        prev_date_str = entry.get("next_date")
        calculate_next_for_entry(entry, today)
        if entry.get("next_date") != prev_date_str:
            changed = True
        data_to_keep.append(entry)

    if changed or len(data_to_keep) != original_len:
        data[:] = data_to_keep
        save_data(data)

def main(): 

#ielādē datus
#atjaunina datumus
#parāda šodienas informāciju
#piedāvā galveno izvēlni un apstrādā lietotāja izvēles.

    data = load_data()
    update_all_dates(data)
    print(f"{Fore.CYAN}♻️  ATKRITUMU GRAFIKA PALĪGS  ♻️{Style.RESET_ALL}")
    today = datetime.date.today()
    print(f"📅 Šodien: {format_date(today)}\n")
    check_today_reminders(data)
    while True:
        print("\n--- GALVENĀ IZVĒLNE ---")
        print("1. Pievienot jaunu izvešanas grafiku")
        print("2. Apskatīt tuvākos izvešanas datumus")
        print("3. Iziet")
        choice = input("> ").strip()
        if choice == "1":
            add_entry(data)
        elif choice == "2":
            view_schedules(data)
        elif choice == "3":
            save_data(data)
            print(f"{Fore.GREEN}💾 Uz redzēšanos! 👋{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.YELLOW}⛔Nepareiza izvēle. Lūdzu mēģiniet vēlreiz.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()