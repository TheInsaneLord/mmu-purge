import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import tkinter.font as tkFont
import json

class MMUGUI:
    def __init__(self, root):
        # Setting title
        root.title("MMU Purge Settings")

        # Setting window size
        width = 600
        height = 500
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
        save_button = tk.Button(root, text="Save", command=self.save_data)
        save_button.place(x=30, y=430, width=125, height=50)

        # Load existing data
        self.mmu_data = self.load_data()
        self.populate_treeview()

        # Event binding for Treeview click
        self.tree.bind("<ButtonRelease-1>", self.on_treeview_click)

    def load_data(self):
        try:
            with open('mmu-db.json', 'r') as file:
                data = json.load(file, object_hook=self.deserialize)
                return {'colors': data.get('colors', []), 'data': data.get('data', {})}
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {'colors': [], 'data': {}}

    def save_data(self):
        try:
            with open('mmu-db.json', 'w') as file:
                json.dump(self.mmu_data, file, indent=2, default=self.serialize)
            messagebox.showinfo("Save", "Data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {e}")

    def populate_treeview(self):
        # Clear existing columns
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")

        # Set new columns based on colors in the data
        columns = ["Color"] + self.mmu_data['colors']
        self.tree["columns"] = tuple(columns)

        for col in columns:
            self.tree.heading(col, text=col)

        # Populate Treeview
        self.tree.delete(*self.tree.get_children())
        for color in self.mmu_data['colors']:
            values = [color] + [self.mmu_data['data'].get((color, col), 'na') for col in self.mmu_data['colors']]
            self.tree.insert("", "end", values=values)

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

                # Update data dictionary
                self.mmu_data['data'][color_row][color_column] = purge_amount
                self.mmu_data['data'][color_column][color_row] = purge_amount

    def add_color(self):
        new_color = self.color_entry.get().strip()
        if new_color and new_color not in self.mmu_data['colors']:
            self.mmu_data['colors'].append(new_color)
            self.mmu_data['data'][new_color] = {color: 0 for color in self.mmu_data['colors']}
            self.populate_treeview()
            self.color_entry.delete(0, tk.END)  # Clear the entry field
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid and unique color.")

    def serialize(self, obj):
        if isinstance(obj, tk.StringVar):
            return obj.get()
        return obj

    def deserialize(self, obj):
        return tk.StringVar(value=obj) if isinstance(obj, str) else obj

if __name__ == "__main__":
    root = tk.Tk()
    mmu_gui = MMUGUI(root)
    root.mainloop()
