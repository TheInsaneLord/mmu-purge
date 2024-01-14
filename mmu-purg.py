import os
import json
from prettytable import PrettyTable
import Levenshtein

MMU_DB_FILE = 'mmu-db.json'

def load_settings():
    try:
        with open(MMU_DB_FILE, 'r') as file:
            settings = json.load(file)
        return settings
    except FileNotFoundError:
        return {}

def save_settings(settings):
    with open(MMU_DB_FILE, 'w') as file:
        json.dump(settings, file, indent=2)

def update_settings(color1, color2, purge_amount):
    settings = load_settings()
    color1_match = find_closest_color(color1, settings.keys())
    color2_match = find_closest_color(color2, settings.keys())

    if color1_match not in settings:
        settings[color1_match] = {}
    if color2_match not in settings:
        settings[color2_match] = {}

    settings[color1_match][color2_match] = purge_amount
    settings[color2_match][color1_match] = purge_amount
    save_settings(settings)  # Save the updated settings

def find_closest_color(target_color, available_colors):
    closest_color = min(available_colors, key=lambda x: Levenshtein.distance(target_color, x))
    return closest_color

def display_all_colors():
    settings = load_settings()
    if settings:
        colors = list(settings.keys())
        
        table = PrettyTable()
        table.field_names = [''] + colors

        for color1 in colors:
            row = [find_closest_color(color1, colors)]
            for color2 in colors:
                purge_amount = settings.get(color1, {}).get(color2, 'na')
                row.append(str(purge_amount))
            table.add_row(row)

        print(table)
    else:
        print("No MMU Purge Settings found.")

def main():
    while True:
        print("\n1. Update MMU Purge Settings")
        print("2. Display All Colors")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            color1 = input("Enter the first color: ")
            color2 = input("Enter the second color: ")
            purge_amount = float(input("Enter the purge amount: "))
            update_settings(color1, color2, purge_amount)
            print("MMU Purge Settings updated successfully!")

        elif choice == '2':
            display_all_colors()

        elif choice == '3':
            break

        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    main()
