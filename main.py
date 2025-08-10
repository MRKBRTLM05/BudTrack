import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

# ======== SETTINGS ========
Window.clearcolor = (0.15, 0.15, 0.18, 1)  # dark background

DATA_FILE = "budtrack_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        if "current_salary" not in data:
            data["current_salary"] = data.get("salary", 0)
        if "categories" not in data:
            data["categories"] = {}

        for cat, val in list(data["categories"].items()):
            if isinstance(val, (int, float)):
                data["categories"][cat] = {
                    "budget": val,
                    "remaining": val,
                    "last_expense": "None",
                    "last_amount": 0
                }
            elif isinstance(val, dict):
                val.setdefault("budget", 0)
                val.setdefault("remaining", val["budget"])
                val.setdefault("last_expense", "None")
                val.setdefault("last_amount", 0)

        if "history" not in data:
            data["history"] = []

        return data

    return {
        "salary": 0,
        "current_salary": 0,
        "categories": {},
        "history": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

class BudTrackApp(App):
    def build(self):
        self.data = load_data()
        self.main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.update_main_screen()
        return self.main_layout

    def update_main_screen(self):
        self.main_layout.clear_widgets()

        # Salary Container
        salary_box = BoxLayout(orientation="vertical", padding=10, spacing=5, size_hint_y=None, height=100)
        with salary_box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.2, 0.4, 0.6, 1)
            self.salary_bg = RoundedRectangle(size=salary_box.size, pos=salary_box.pos, radius=[10])
        salary_box.bind(size=lambda *x: setattr(self.salary_bg, 'size', salary_box.size))
        salary_box.bind(pos=lambda *x: setattr(self.salary_bg, 'pos', salary_box.pos))

        salary_box.add_widget(Label(text=f"💵 Salary: ₱{self.data['salary']}", font_size=20, color=(1,1,1,1)))
        salary_box.add_widget(Label(text=f"💰 Current Salary: ₱{self.data['current_salary']}", font_size=20, color=(1,1,1,1)))
        self.main_layout.add_widget(salary_box)

        # Categories Container
        category_scroll = ScrollView(size_hint=(1, None), size=(self.main_layout.width, 400))
        category_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        category_layout.bind(minimum_height=category_layout.setter('height'))

        for cat, details in self.data["categories"].items():
            cat_box = BoxLayout(orientation="vertical", padding=8, spacing=2, size_hint_y=None, height=110)
            with cat_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.25, 0.25, 0.3, 1)
                cat_bg = RoundedRectangle(size=cat_box.size, pos=cat_box.pos, radius=[8])
            cat_box.bind(size=lambda inst, val, bg=cat_bg: setattr(bg, 'size', inst.size))
            cat_box.bind(pos=lambda inst, val, bg=cat_bg: setattr(bg, 'pos', inst.pos))

            cat_box.add_widget(Label(text=f"📂 {cat} - Budget: ₱{details['budget']}", color=(1,1,1,1)))
            cat_box.add_widget(Label(text=f"Last Expense: {details['last_expense']} - ₱{details['last_amount']}", color=(0.9,0.9,0.9,1)))
            cat_box.add_widget(Label(text=f"Remaining: ₱{details['remaining']}", color=(0.5,1,0.5,1)))
            category_layout.add_widget(cat_box)

        category_scroll.add_widget(category_layout)
        self.main_layout.add_widget(category_scroll)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        btn_layout.add_widget(Button(text="➕ Add Expense", background_color=(0.1,0.6,0.3,1), on_press=self.add_expense_popup))
        btn_layout.add_widget(Button(text="⚙ Setup Budget", background_color=(0.2,0.5,0.8,1), on_press=self.setup_popup))
        btn_layout.add_widget(Button(text="📜 View Report", background_color=(0.6,0.4,0.2,1), on_press=self.show_report))
        btn_layout.add_widget(Button(text="🗑 Clear Data", background_color=(0.8,0.2,0.2,1), on_press=self.clear_data_popup))
        self.main_layout.add_widget(btn_layout)

    def clear_data_popup(self, instance):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        years = [str(y) for y in range(2020, datetime.now().year + 2)]

        month_spinner = Spinner(text=months[datetime.now().month - 1], values=months, size_hint_y=None, height=40)
        year_spinner = Spinner(text=str(datetime.now().year), values=years, size_hint_y=None, height=40)

        def confirm_clear(instance):
            month = month_spinner.text
            year = year_spinner.text
            confirm_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
            confirm_layout.add_widget(Label(text=f"Are you sure you want to delete all data for {month} {year}?", color=(1,1,1,1)))

            def do_clear(instance):
                self.data = {
                    "salary": 0,
                    "current_salary": 0,
                    "categories": {},
                    "history": [h for h in self.data["history"] if not h["date"].startswith(f"{year}-{months.index(month)+1:02d}")]
                }
                save_data(self.data)
                confirm_popup.dismiss()
                popup.dismiss()
                self.update_main_screen()

            confirm_layout.add_widget(Button(text="Yes, Delete", background_color=(0.8,0.2,0.2,1), on_press=do_clear))
            confirm_layout.add_widget(Button(text="Cancel", background_color=(0.3,0.3,0.3,1), on_press=lambda x: confirm_popup.dismiss()))

            confirm_popup = Popup(title="Confirm Deletion", content=confirm_layout, size_hint=(0.8, 0.4))
            confirm_popup.open()

        layout.add_widget(Label(text="Select Month and Year to Clear", color=(1,1,1,1)))
        layout.add_widget(month_spinner)
        layout.add_widget(year_spinner)
        layout.add_widget(Button(text="Next", background_color=(0.8,0.5,0.2,1), on_press=confirm_clear))

        popup = Popup(title="Clear Monthly Data", content=layout, size_hint=(0.8, 0.5))
        popup.open()

    def setup_popup(self, instance):
        layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        salary_input = TextInput(text=str(self.data["salary"]), hint_text="Enter Salary", multiline=False)
        category_inputs = []

        def add_category_field(name="", budget=""):
            cat_layout = BoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=40)
            name_input = TextInput(text=name, hint_text="Category Name", multiline=False)
            budget_input = TextInput(text=str(budget), hint_text="Budget", multiline=False)
            cat_layout.add_widget(name_input)
            cat_layout.add_widget(budget_input)
            category_inputs.append((name_input, budget_input))
            category_box.add_widget(cat_layout)

        category_box = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
        add_category_field()
        add_category_field()
        add_category_field()

        def add_category_row(instance):
            add_category_field()

        add_cat_btn = Button(text="➕ Add Category", size_hint_y=None, height=40, background_color=(0.1,0.5,0.8,1))
        add_cat_btn.bind(on_press=add_category_row)

        def save_setup(instance):
            salary = float(salary_input.text)
            self.data["salary"] = salary
            self.data["current_salary"] = salary

            categories = {}
            for name_input, budget_input in category_inputs:
                if name_input.text.strip():
                    b = float(budget_input.text)
                    categories[name_input.text.strip()] = {
                        "budget": b,
                        "remaining": b,
                        "last_expense": "None",
                        "last_amount": 0
                    }
            self.data["categories"] = categories
            save_data(self.data)
            popup.dismiss()
            self.update_main_screen()

        layout.add_widget(Label(text="Setup Salary & Categories", color=(1,1,1,1)))
        layout.add_widget(salary_input)
        layout.add_widget(category_box)
        layout.add_widget(add_cat_btn)
        layout.add_widget(Button(text="Save", background_color=(0.1,0.6,0.3,1), on_press=save_setup))

        popup = Popup(title="Setup Budget", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def add_expense_popup(self, instance):
        layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        name_input = TextInput(hint_text="Expense name", multiline=False)
        amount_input = TextInput(hint_text="Amount", multiline=False)

        category_names = list(self.data["categories"].keys())
        if not category_names:
            popup = Popup(title="Error", content=Label(text="No categories set up yet!", color=(1,1,1,1)), size_hint=(0.8, 0.3))
            popup.open()
            return

        category_spinner = Spinner(text="Select Category", values=category_names)

        def save_expense(instance):
            amount = float(amount_input.text)
            category = category_spinner.text
            if category in self.data["categories"]:
                self.data["categories"][category]["remaining"] -= amount
                self.data["categories"][category]["last_expense"] = name_input.text
                self.data["categories"][category]["last_amount"] = amount
                self.data["current_salary"] -= amount
                self.data["history"].append({
                    "name": name_input.text,
                    "amount": amount,
                    "category": category,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(self.data)
                popup.dismiss()
                self.update_main_screen()

        layout.add_widget(Label(text="Add New Expense", color=(1,1,1,1)))
        layout.add_widget(name_input)
        layout.add_widget(amount_input)
        layout.add_widget(category_spinner)
        layout.add_widget(Button(text="Save", background_color=(0.1,0.6,0.3,1), on_press=save_expense))

        popup = Popup(title="Add Expense", content=layout, size_hint=(0.9, 0.7))
        popup.open()

    def show_report(self, instance):
        layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        total_spent = sum(h["amount"] for h in self.data["history"])
        savings = self.data["salary"] - total_spent

        layout.add_widget(Label(text=f"Total Spent: ₱{total_spent}", color=(1,0.5,0.5,1)))
        layout.add_widget(Label(text=f"Savings: ₱{savings}", color=(0.5,1,0.5,1)))

        for h in self.data["history"]:
            layout.add_widget(Label(text=f"{h['date']} - {h['name']}: ₱{h['amount']} ({h['category']})", color=(1,1,1,1)))

        popup = Popup(title="Monthly Report", content=layout, size_hint=(0.9, 0.9))
        popup.open()

if __name__ == "__main__":
    BudTrackApp().run()
