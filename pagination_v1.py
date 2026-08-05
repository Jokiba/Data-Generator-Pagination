
"""
Prikaz funkcionalnosti skripte
[Page 1/60] [Total rows: 5000]
+------------+-------------+-----------------+--------------+------------+
| vlasnik_id | vlasnik_ime | vlasnik_prezime | mesto        | datum_reg  |
+------------+-------------+-----------------+--------------+------------+
|          1 | Vladimir    | Perić           | Laćarak      | 2026-09-12 |
|          2 | Milan       | Maričić         | Bosut        | 2027-02-15 |
|          3 | Nikola      | Jovanović       | Jarak        | 2027-04-28 |
+------------+--------------+----------------+--------------+------------+
[P]revious  [N]ext  [G]o To  [D]etails  [Q]uit
"""

import pymysql
import time
import sys
import math
import subprocess
import os
from tabulate import tabulate

db_credential = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": None,
    "database": "db_vozila",
    "charset": "utf8mb4"
}
# funkcija za konektovanje sa bazom
def connect() -> pymysql.Connection:
    return pymysql.connect(**db_credential)

# funkcija za rekonekciju ako je veza prekinuta
# union operator | može da vrati pymysql.Connection ili objekat tipa bool
def reconnect() -> pymysql.Connection|bool:
    for _ in range(3):
        try:
            connection = connect()
            return connection
        except:
            time.sleep(1)
    return False

# funkcija za dohvatanje podataka iz tabele
def get_people_data(connection: pymysql.Connect, limit= 25, offset= 0):
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT vl.vlasnik_id, vl.vlasnik_ime, vl.vlasnik_prezime, vl.adresa, 
                           vl.mesto, vo.datum_reg FROM vlasnik_vozila vl INNER JOIN vozila vo 
                           USING(vlasnik_id)
                           WHERE vo.datum_reg != 'None'
                           ORDER BY vo.datum_reg ASC 
                           LIMIT {limit} OFFSET {offset};
                        """)
        data_result = cursor.fetchall()
        return data_result if data_result else []

# funkcija za dohvatanje broja zapisa
def get_total_rows(connection: pymysql.Connect):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT COUNT(datum_reg) AS reg_vozila FROM vozila
                          WHERE datum_reg != 'None';""")
        result_set = cursor.fetchone()
        # ovde sam izmenio u zagrade 0 umesto 'number_people' 
        return result_set[0] if result_set[0] else 0

# prikaz informacija o vozilu vlasnika
def get_vehicle_details(connection: pymysql.Connect, owner_id):
    with connection.cursor() as cursor:
        cursor.execute(f""" SELECT vlasnik_id, marka, model, godiste, motor_kw, reg_oznaka 
                           FROM vozila WHERE vlasnik_id = {owner_id};
                       """)
        vehicle_data = cursor.fetchall()
        return vehicle_data if vehicle_data else []
# testiranje konekcije
"""
Ako je uspešno prošla test konekcija sama će se zatvoriti kada nema dalji kod u sebi.
"""
if __name__ == "__main__":
    try:
        connect()
        print("Test connection successfully established.")
    except:
        print("Error establishing test connection!")
        sys.exit()
    
    # posle test konekcije radimo pravu konekciju smeštamo je u objekat
    connection = connect()
    # interaktivna aplikacija gde korisniku prikazujemo podatke
    limit = 25
    offset = 0
    page = 1
    total_rows = get_total_rows(connection)
    total_pages = math.ceil(total_rows / limit)

    if not connection.open:
        connection = reconnect()
        if not connection:
            print("Failed to reconnect after 3 attempts. Shutting down!")
            sys.exit(1)
    while True:
        vehicle_owners = get_people_data(connection, limit, offset)

        print(tabulate(vehicle_owners, headers=["ID Vlasnik", "Ime", "Prezime", "Adresa", 
                                                "Mesto", "Datum Reg."], tablefmt="github"))
        print(f"[Page {page}/{total_pages}] [Total rows: {total_rows}]")      
        print("------- [P]revious, [N]ext, [G]o To, [D]etails, [Q]uit + [⏎ Enter]")
        choice = input("Input your choice: ").strip()
        subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
       
        if choice.lower() == "q":
            sys.exit(0)
        elif choice.lower() == "n":
            if page + 1 > total_pages:
                print("There is no next page!")
                input("----- Press [Enter ⏎] to continue...")
            else:
                offset += limit
                page += 1
            
        elif choice.lower() == "p":
            if page - 1 == 0:
                print("There is no previous page.")
                input("----- Press [Enter ⏎] to continue...")
            else:
                offset -= limit
                page -= 1
        elif choice.lower() == "g":
            page_num = int(input("Input page number: "))
            if page_num > total_pages or page_num < 1:
                print(f"There is no page with that number: {page_num}")
                input("----- Press [Enter ⏎] to continue...")
            else:
                page = page_num
                offset = (page - 1) * limit
        elif choice.lower() == "d":
            owner_id = int(input("Input owner id for vehicle details: "))
            vehicle_details = get_vehicle_details(connection, owner_id)
            print(tabulate(vehicle_details, headers=["ID Vlasnik", "Marka", "Model", "God.", 
                                                     "Kw", "Tablice"], tablefmt="github"))
            input("----- Press [Enter ⏎] to continue...")
