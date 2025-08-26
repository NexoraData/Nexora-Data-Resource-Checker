import json
import csv
import os
import multiprocessing
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import datetime
import re

def load_requirements(requirements_file):
    requirements = {}
    if not os.path.exists(requirements_file):
        print(f"Requirements file not found: {requirements_file}")
        return requirements
    with open(requirements_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            resource, package_id = line.split(":", 1)
            requirements[resource.strip()] = package_id.strip()
    return requirements

def load_customer_packages(csv_folder):
    user_packages = {}
    csv_files = list(Path(csv_folder).glob("*.csv"))
    if not csv_files:
        print("No CSV files found in customers folder!")
        return user_packages
    with open(csv_files[0], "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row.get("Username", "").strip()
            packages_field = row.get("Packages", "").strip()
            if not username:
                continue
            username = username.lower()
            clean_field = packages_field.replace("[", "").replace("]", "").replace('"', "")
            clean_field = clean_field.replace(";", ",")
            owned_packages = set(re.split(r"[,\s]+", clean_field))
            owned_packages = {p.strip() for p in owned_packages if p.strip()}
            if username not in user_packages:
                user_packages[username] = set()
            user_packages[username].update(owned_packages)
    return user_packages

def process_json_file(args):
    json_file, requirements, user_packages = args
    unauthorized_servers = []
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            server_resources = data.get("Data", {}).get("resources", [])
            owner_name = data.get("Data", {}).get("ownerName", "N/A")
            owner_profile = data.get("Data", {}).get("ownerProfile", "N/A")
            server_code = data.get("EndPoint", "N/A")
            owner_key = owner_name.lower()
            for resource, required_package in requirements.items():
                if resource in server_resources:
                    owner_owned = user_packages.get(owner_key, set())
                    if required_package not in owner_owned:
                        unauthorized_servers.append({
                            "server_code": server_code,
                            "owner_name": owner_name,
                            "owner_profile": owner_profile,
                            "resource": resource,
                            "required_package": required_package,
                            "file_name": json_file.name
                        })
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return [], f"Error reading {json_file.name}: {str(e)}"
    except Exception as e:
        return [], f"Unexpected error with {json_file.name}: {str(e)}"
    return unauthorized_servers, None

def scan_servers_parallel(servers_folder, requirements, user_packages):
    json_files = list(Path(servers_folder).glob("*.json"))
    total_files = len(json_files)
    if total_files == 0:
        print("No JSON files found in servers folder!")
        return [], 0, 0
    print(f"Found {total_files} JSON files. Starting scan...")
    args_list = [(file, requirements, user_packages) for file in json_files]
    unauthorized_servers = []
    processed_files = 0
    found_servers = 0
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        future_to_file = {executor.submit(process_json_file, args): args[0] for args in args_list}
        for future in as_completed(future_to_file):
            processed_files += 1
            result, error = future.result()
            if error:
                print(f"  {error}")
            if result:
                found_servers += len(result)
                unauthorized_servers.extend(result)
            progress = (processed_files / total_files) * 100
            print(f"\rProcessed: {processed_files}/{total_files} files ({progress:.1f}%) | Found: {found_servers} unauthorized servers", end="")
    print()
    return unauthorized_servers, processed_files, found_servers

def save_results_to_file(unauthorized_servers, requirements):
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/5DB-Check-ID_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("UNAUTHORIZED SERVERS REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Requirements Checked: {len(requirements)} resources\n")
        f.write(f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Unauthorized Servers Found: {len(unauthorized_servers)}\n")
        f.write("=" * 80 + "\n\n")
        if unauthorized_servers:
            for server in unauthorized_servers:
                f.write(f"Server Code: {server['server_code']}\n")
                f.write(f"Owner Name: {server['owner_name']}\n")
                f.write(f"Owner Profile: {server['owner_profile']}\n")
                f.write(f"Resource: {server['resource']}\n")
                f.write(f"Required Package: {server['required_package']}\n")
                f.write(f"JSON File: {server['file_name']}\n")
                f.write("-" * 40 + "\n")
        else:
            f.write("No unauthorized servers found!\n")
    return filename

def main():
    print("Loading requirements...")
    requirements = load_requirements("Requirements/Requirements.txt")
    print(f"Loaded {len(requirements)} requirements")
    print("Loading customer packages...")
    user_packages = load_customer_packages("customers")
    print(f"Loaded {len(user_packages)} customer records")
    print("Scanning servers for unauthorized usage...")
    start_time = time.time()
    unauthorized_servers, processed_files, found_servers = scan_servers_parallel("servers", requirements, user_packages)
    end_time = time.time()
    print(f"Scan completed in {end_time - start_time:.2f} seconds")
    print(f"Processed {processed_files} files, found {found_servers} unauthorized servers")
    output_file = save_results_to_file(unauthorized_servers, requirements)
    print(f"Results saved to: {output_file}")
    if unauthorized_servers:
        print("\n" + "="*80)
        print("UNAUTHORIZED SERVERS FOUND:")
        print("="*80)
        for server in unauthorized_servers:
            print(f"Server Code: {server['server_code']}")
            print(f"Owner Name: {server['owner_name']}")
            print(f"Owner Profile: {server['owner_profile']}")
            print(f"Resource: {server['resource']}")
            print(f"Required Package: {server['required_package']}")
            print(f"JSON File: {server['file_name']}")
            print("-" * 40)
    else:
        print("\nNo unauthorized servers found!")

if __name__ == "__main__":
    print(r"""
     .-') _   ('-.  ) (`-.                 _  .-')     ('-.    
    ( OO ) )_(  OO)  ( OO ).              ( \( -O )   ( OO ).-.
,--./ ,--,'(,------.(_/.  \_)-..-'),-----. ,------.   / . --. /
|   \ |  |\ |  .---' \  `.'  /( OO'  .-.  '|   /`. '  | \-.  \ 
|    \|  | )|  |      \     /\/   |  | |  ||  /  | |.-'-'  |  |
|  .     |/(|  '--.    \   \ |\_) |  |\|  ||  |_.' | \| |_.'  |
|  |\    |  |  .--'   .'    \_) \ |  | |  ||  .  '.'  |  .-.  |
|  | \   |  |  `---. /  .'.  \   `'  '-'  '|  |\  \   |  | |  |
`--'  `--'  `------''--'   '--'    `-----' `--' '--'  `--' `--'

Created By : sophia.c33
All Rights are held by : Nexora Data Limited
This holds a License under the Nexora Data License
---
""")
    main()