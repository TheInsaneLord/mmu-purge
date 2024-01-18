import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import tkinter.font as tkFont
import os
import json

config_file_path = os.path.expanduser(os.path.join("~/Documents/mmu-purge", "config.json"))
mmu_data_file = os.path.expanduser(os.path.join("~/Documents/mmu-purge", "mmu-data.txt"))
ver_num = 1.2

#print(mmu_data_path)
print(mmu_data_file)
print(" ")

class SettingsDialog(tk.simpledialog.Dialog):
    def __init__(self, parent):
        self.config = load_config()
        super().__init__(parent)

    def body(self, master):
        tk.Label(master, text="Data File Path:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Window Width:").grid(row=1, sticky=tk.W)
        tk.Label(master, text="Window Height:").grid(row=2, sticky=tk.W)

        self.data_file_path_entry = tk.Entry(master)
        self.window_width_entry = tk.Entry(master)
        self.window_height_entry = tk.Entry(master)

        self.data_file_path_entry.grid(row=0, column=1)
        self.window_width_entry.grid(row=1, column=1)
        self.window_height_entry.grid(row=2, column=1)

        # Set default values
        self.data_file_path_entry.insert(0, self.config.get("data_file_path", ""))
        self.window_width_entry.insert(0, str(self.config.get("width", 600)))
        self.window_height_entry.insert(0, str(self.config.get("height", 500)))

    def apply(self):
        data_file_path = self.data_file_path_entry.get()
        width = int(self.window_width_entry.get())
        height = int(self.window_height_entry.get())

        # Save settings to config file
        save_config(data_file_path, width, height)

        # Apply the changes to the application
        root.geometry(f"{width}x{height}")
        global mmu_data_file
        mmu_data_file = os.path.join(data_file_path, "mmu-data.txt")

        # Reload data
        mmu_gui.load_data_from_txt()
        mmu_gui.populate_treeview()

def check_conf_exists():
    print("Checking conf file exists at {}".format(config_file_path))
    try:
        if not os.path.exists(config_file_path):
            print("Config file not found. Creating default config")
            default_config = {
                "data_file_path": "~/Documents/mmu-purge",
                "width": 600,
                "height": 500
            }
            with open(config_file_path, 'w') as f:
                json.dump(default_config, f, indent=4)
        else:
            print("Config file found")
    except Exception as e:
        print("Error creating default config:", str(e))

def load_config():
    try:
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
    return config

def save_config(data_file_path, width, height):
    config = {
        "data_file_path": data_file_path,
        "width": width,
        "height": height
    }
    with open(config_file_path, 'w') as config_file:
        json.dump(config, config_file)

class MMUGUI:
    def __init__(self, root):
        self.mmu_data = {}
        self.create_menu(root)

        # Setting title
        root.title("MMU Purge Settings v{}".format(str(ver_num)))

        # Setting window size
        self.config = load_config()
        width = self.config.get("width", 600)
        height = self.config.get("height", 500)
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # Create Treeview
        self.tree = ttk.Treeview(root, show='headings')
        self.tree["columns"] = ("Color",)
        self.tree.heading("Color", text="Color")
        self.tree.column("Color", width=100, anchor='center')
        self.tree.place(x=30, y=30, width=537, height=322)

        # Add Color Entry
        text_color_entry = tk.Label(root, text='Enter colour to add:')
        text_color_entry.place(x=150, y=370, width=150, height=50)
        self.color_entry = tk.Entry(root, borderwidth="1px")
        self.color_entry.place(x=290, y=370, width=276, height=50)

        # Add Color Button
        add_color_button = tk.Button(root, text="Add Color", command=self.add_color)
        add_color_button.place(x=30, y=370, width=125, height=50)

        # Save Button
        save_button = tk.Button(root, text="Save", command=self.save_data_to_txt)
        save_button.place(x=30, y=430, width=125, height=50)

        # Load Button
        load_button = tk.Button(root, text="Load", command=self.load_data_from_txt)
        load_button.place(x=160, y=430, width=125, height=50)

        # Load existing data
        self.load_data_from_txt()
        self.populate_treeview()

        # Event binding for Treeview click
        self.tree.bind("<ButtonRelease-1>", self.on_treeview_click)


    def create_menu(self, root):
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change Settings", command=self.open_settings_dialog)

    def open_settings_dialog(self):
        dialog = SettingsDialog(root)

    def save_data_to_txt(self):
        try:
            with open(mmu_data_file, 'w') as file:
                for color, relationships in self.mmu_data.items():
                    relationships_str = " - ".join([f"{key}:{value}" for key, value in relationships.items()])
                    file.write(f"{color} | {relationships_str}\n")
            messagebox.showinfo("Save", "Data saved successfully to \n{}.".format(mmu_data_file))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {e}")

    def load_data_from_txt(self):
        mmu_data = {}
        try:
            if os.path.exists(mmu_data_file):
                print(f"Data File found")
                with open(mmu_data_file, 'r') as file:
                    for line in file:
                        color, relationships_str = line.strip().split(" | ")
                        relationships = {pair.split(":")[0]: int(pair.split(":")[1]) for pair in relationships_str.split(" - ")}
                        mmu_data[color] = relationships
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}

        # Update self.mmu_data and populate the Treeview
        self.mmu_data = mmu_data
        self.populate_treeview()

        return mmu_data

    def populate_treeview(self):
        # Clear existing columns
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
            self.tree.column(col, width=1)  # Set initial column width to 1

        # Set new columns based on colors in the data
        columns = ["Color"] + list(self.mmu_data.keys())
        self.tree["columns"] = tuple(columns)

        for col in columns:
            self.tree.heading(col, text=col)

        # Populate Treeview
        self.tree.delete(*self.tree.get_children())
        for color, relationships in self.mmu_data.items():
            row_values = [color] + [relationships.get(col, 'n/a') for col in self.mmu_data.keys()]
            self.tree.insert("", "end", values=row_values)

        # Adjust column widths based on content
        for col in columns:
            self.tree.column(col, width=tkFont.Font().measure(col) + 20)  # Adding a small margin

    def on_treeview_click(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            color_row = self.tree.item(item, 'values')[0]

            # Find the column based on the x-coordinate of the click
            column_id = self.tree.identify_column(event.x)
            if column_id and column_id != "#0":  # Exclude the first (index) column
                color_column = self.tree.heading(column_id, 'text')
                color_column = color_column if color_column != "" else color_row  # If column heading is empty, use row color

                # Prompt user to enter purge amount
                purge_amount = simpledialog.askinteger("Purge Amount",
                                                    f"Enter purge amount for {color_row} to {color_column} (in mm):",
                                                    parent=root, minvalue=0)

                # Update Treeview with new purge amount
                self.tree.set(item, column_id, purge_amount)

                # Update data dictionary for the edited columns
                self.mmu_data[color_row][color_column] = purge_amount
                self.mmu_data[color_column][color_row] = purge_amount

                # Synchronize changes between two columns
                for col in self.mmu_data.keys():
                    if col != color_row and col != color_column:
                        shared_value = self.mmu_data[color_row][col]
                        self.mmu_data[col][color_row] = shared_value
                        self.mmu_data[color_row][col] = shared_value

                        shared_value = self.mmu_data[color_column][col]
                        self.mmu_data[col][color_column] = shared_value
                        self.mmu_data[color_column][col] = shared_value

                # Call populate_treeview to update the Treeview immediately
                self.populate_treeview()

    def add_color(self):
        new_color = self.color_entry.get().strip()
        if new_color and new_color not in self.mmu_data:
            self.mmu_data[new_color] = {color: 0 for color in self.mmu_data.keys()}
            self.populate_treeview()
            self.color_entry.delete(0, tk.END)  # Clear the entry field
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid and unique color.")

if __name__ == "__main__":
    check_conf_exists()
    root = tk.Tk()
    mmu_gui = MMUGUI(root)
    root.mainloop()
