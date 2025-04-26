import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Date picker support
try:
    from tkcalendar import DateEntry

    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

DB_FILE = 'finance_tracker.db'
CURRENCIES = ['USD', 'EUR', 'INR', 'GBP', 'JPY']


# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Categories
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL
    )''')
    # Transactions
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        type TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')
    # Subscriptions
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        category_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        frequency TEXT NOT NULL,
        next_due TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')
    # Settings (for currency)
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    # Default categories
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Salary', 'Income')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Investment', 'Income')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Freelance', 'Income')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Rental Income', 'Income')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Business Income', 'Income')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Bonus', 'Income')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Interest', 'Income')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Dividend', 'Income')")

    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Food', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Rent', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Utilities', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Transportation', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Entertainment', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Shopping', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Healthcare', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Insurance', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Education', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Travel', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Groceries', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Home Maintenance', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Clothing', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Personal Care', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Subscriptions', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Phone Bill', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Internet', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Gym Membership', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Dining Out', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Gifts', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Pet Care', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Taxes', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Loan Payment', 'Expense')")
    c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES ('Miscellaneous', 'Expense')")
    # Default currency
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', 'USD')")
    conn.commit()

    # Debug: Check categories were inserted
    c.execute("SELECT COUNT(*) FROM categories")
    count = c.fetchone()[0]
    print(f"Database initialized with {count} categories")

    conn.close()


# --- DB HELPERS ---
def get_currency():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='currency'")
    res = c.fetchone()
    conn.close()
    return res[0] if res else 'USD'


def set_currency(curr):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('currency', ?)", (curr,))
    conn.commit()
    conn.close()


# --- GUI ---
from tkinter import font as tkfont


class FinanceTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Finance Tracker')
        self.geometry('1000x700')
        self.conn = sqlite3.connect(DB_FILE)
        self.currency = get_currency()
        self.style = ttk.Style(self)
        self.configure_styles()
        import matplotlib
        matplotlib.use('TkAgg')
        self.create_widgets()
        # Important: Make sure to refresh categories after creating widgets
        self.refresh_all()
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def on_close(self):
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except Exception:
            pass
        self.destroy()

    def configure_styles(self):
        self.style.theme_use('clam')
        # Modern, simple color palette
        self.style.configure('TFrame', background='#f7f9fb')
        self.style.configure('TLabel', background='#f7f9fb', font=('Segoe UI', 10))
        self.style.configure('TLabelFrame', background='#f7f9fb', font=('Segoe UI', 10, 'bold'))
        self.style.configure('TNotebook', background='#f7f9fb', tabposition='n')
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 11, 'bold'), padding=10)
        self.style.configure('TEntry', font=('Segoe UI', 10), relief='flat', borderwidth=1)
        self.style.configure('TCombobox', font=('Segoe UI', 10), relief='flat', borderwidth=1)
        # Round-cornered, modern buttons
        self.style.configure('TButton', font=('Segoe UI', 10), padding=8, relief='flat', borderwidth=0,
                             background='#e0e7ef', foreground='#222')
        self.style.map('TButton', background=[('active', '#d0e2f2')],
                       relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), background='#4f8cff', foreground='white',
                             padding=10, relief='flat', borderwidth=0)
        self.style.map('Accent.TButton', background=[('active', '#2563eb')],
                       relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        # Custom style for Edit/Delete buttons (blue background, white text)
        self.style.configure('Blue.TButton', background='#2563eb', foreground='white', font=('Segoe UI', 10, 'bold'))
        self.style.map('Blue.TButton', background=[('active', '#1d4ed8')], foreground=[('active', 'white')])
        self.style.configure('Modern.Treeview', font=('Segoe UI', 10), rowheight=28, fieldbackground='#fff',
                             borderwidth=0)
        self.style.map('Modern.Treeview', background=[('selected', '#e6f0fa')])
        # Card style for dashboard
        self.style.configure('Card.TLabelframe', background='#eaf6fb', foreground='#333', borderwidth=2,
                             relief='groove')
        self.style.configure('Card.TLabelframe.Label', font=('Segoe UI', 11, 'bold'), background='#eaf6fb',
                             foreground='#0078d7')

    def create_widgets(self):
        # Tabs
        self.tabs = ttk.Notebook(self)
        # Dashboard Tab
        self.tab_dashboard = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_dashboard, text='🏠 Dashboard')

        # --- Dashboard Tab ---
        # Date Range Picker
        dash_range_frame = ttk.Frame(self.tab_dashboard)
        dash_range_frame.pack(fill='x', padx=20, pady=(10, 0))
        ttk.Label(dash_range_frame, text='Dashboard Date Range:', font=('Segoe UI', 10, 'bold')).pack(side='left')
        self.dash_date_range = tk.StringVar(value='This Month')
        self.dash_range_combo = ttk.Combobox(dash_range_frame, textvariable=self.dash_date_range, state='readonly',
                                             width=15,
                                             values=['This Month', 'Last Month', 'Last 3 Months', 'This Year',
                                                     'Custom...'])
        self.dash_range_combo.pack(side='left', padx=8)
        self.dash_range_combo.bind('<<ComboboxSelected>>', self.on_dashboard_range_change)

        # Custom date entry (hidden by default, shown if "Custom..." is selected)
        if TKCALENDAR_AVAILABLE:
            self.dash_custom_start = DateEntry(dash_range_frame, width=12, date_pattern='yyyy-mm-dd')
            self.dash_custom_end = DateEntry(dash_range_frame, width=12, date_pattern='yyyy-mm-dd')
            self.dash_custom_start.set_date(datetime.now().replace(day=1))
            self.dash_custom_end.set_date(datetime.now())
        else:
            self.dash_custom_start = ttk.Entry(dash_range_frame, width=12)
            self.dash_custom_end = ttk.Entry(dash_range_frame, width=12)
            self.dash_custom_start.insert(0, 'YYYY-MM-DD')
            self.dash_custom_end.insert(0, 'YYYY-MM-DD')
        self.dash_custom_start.pack_forget()
        self.dash_custom_end.pack_forget()
        # Will be managed in refresh_dashboard

        dash_card_frame = ttk.Frame(self.tab_dashboard)
        dash_card_frame.pack(fill='x', padx=20, pady=20)
        # Summary cards
        card_style = {'relief': 'groove', 'borderwidth': 2, 'padding': 16}
        self.dash_card_income = ttk.LabelFrame(dash_card_frame, text='💰 Income', style='Card.TLabelframe', **card_style)
        self.dash_card_income.pack(side='left', expand=True, fill='x', padx=8)
        self.dash_card_expense = ttk.LabelFrame(dash_card_frame, text='💸 Expense', style='Card.TLabelframe',
                                                **card_style)
        self.dash_card_expense.pack(side='left', expand=True, fill='x', padx=8)
        self.dash_card_balance = ttk.LabelFrame(dash_card_frame, text='💼 Net Balance', style='Card.TLabelframe',
                                                **card_style)
        self.dash_card_balance.pack(side='left', expand=True, fill='x', padx=8)
        self.dash_card_savings = ttk.LabelFrame(dash_card_frame, text='📈 Savings Rate', style='Card.TLabelframe',
                                                **card_style)
        self.dash_card_savings.pack(side='left', expand=True, fill='x', padx=8)
        # Card values
        self.dash_income_val = ttk.Label(self.dash_card_income, text='', font=('Segoe UI', 16, 'bold'))
        self.dash_income_val.pack()
        self.dash_expense_val = ttk.Label(self.dash_card_expense, text='', font=('Segoe UI', 16, 'bold'))
        self.dash_expense_val.pack()
        self.dash_balance_val = ttk.Label(self.dash_card_balance, text='', font=('Segoe UI', 16, 'bold'))
        self.dash_balance_val.pack()
        self.dash_savings_val = ttk.Label(self.dash_card_savings, text='', font=('Segoe UI', 16, 'bold'))
        self.dash_savings_val.pack()
        # Savings Goal Widget
        self.dash_goal_frame = ttk.LabelFrame(self.tab_dashboard, text='🎯 Savings Goal', style='Card.TLabelframe')
        self.dash_goal_frame.pack(fill='x', padx=20, pady=(0, 10))
        self.dash_goal_label = ttk.Label(self.dash_goal_frame, text='Set your savings goal:',
                                         font=('Segoe UI', 10, 'bold'))
        self.dash_goal_label.pack(side='left', padx=10)
        self.dash_goal_amount = ttk.Entry(self.dash_goal_frame, width=10)
        self.dash_goal_amount.pack(side='left', padx=5)
        self.dash_goal_set_btn = ttk.Button(self.dash_goal_frame, text='Set Goal', style='Accent.TButton',
                                            command=self.set_savings_goal)
        self.dash_goal_set_btn.pack(side='left', padx=5)
        self.dash_goal_progress = ttk.Progressbar(self.dash_goal_frame, length=200, mode='determinate')
        self.dash_goal_progress.pack(side='left', padx=15)
        self.dash_goal_status = ttk.Label(self.dash_goal_frame, text='', font=('Segoe UI', 10, 'bold'))
        self.dash_goal_status.pack(side='left', padx=5)
        # Net Worth Card
        self.dash_networth_frame = ttk.LabelFrame(self.tab_dashboard, text='💼 Net Worth', style='Card.TLabelframe')
        self.dash_networth_frame.pack(fill='x', padx=20, pady=(0, 10))
        self.dash_networth_label = ttk.Label(self.dash_networth_frame, text='', font=('Segoe UI', 14, 'bold'),
                                             foreground='#0078d7')
        self.dash_networth_label.pack(padx=10, pady=5)
        # Trends & Insights
        self.dash_trends_frame = ttk.LabelFrame(self.tab_dashboard, text='📊 Trends & Insights',
                                                style='Card.TLabelframe')
        self.dash_trends_frame.pack(fill='x', padx=20, pady=(0, 10))
        self.dash_trends_label = ttk.Label(self.dash_trends_frame, text='', font=('Segoe UI', 10, 'italic'))
        self.dash_trends_label.pack(padx=10, pady=5)
        # Quick Add Buttons
        dash_btn_frame = ttk.Frame(self.tab_dashboard)
        dash_btn_frame.pack(pady=(0, 10))
        ttk.Button(dash_btn_frame, text='➕ Add Transaction', style='Accent.TButton',
                   command=lambda: self.tabs.select(self.tab_transactions)).pack(side='left', padx=10)

        # Recent Activity + Chart (side by side)
        dash_recent_chart_frame = ttk.Frame(self.tab_dashboard)
        dash_recent_chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
        dash_recent_chart_frame.columnconfigure(0, weight=1)
        dash_recent_chart_frame.columnconfigure(1, weight=1)
        dash_recent_chart_frame.rowconfigure(0, weight=1)
        # Left: Recent Activity
        left_recent_frame = ttk.Frame(dash_recent_chart_frame)
        left_recent_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=0)
        ttk.Label(left_recent_frame, text='Recent Activity', font=('Segoe UI', 12, 'bold')).pack(anchor='w',
                                                                                                 pady=(0, 5))
        self.dash_recent = ttk.Treeview(left_recent_frame, columns=('type', 'category', 'amount', 'date', 'desc'),
                                        show='headings', height=8, style='Modern.Treeview')
        for col, label in zip(['type', 'category', 'amount', 'date', 'desc'],
                              ['Type', 'Category', 'Amount', 'Date', 'Description']):
            self.dash_recent.heading(col, text=label)
        self.dash_recent.pack(fill='both', expand=True)
        # Right: Last 3 months spending chart
        right_chart_frame = ttk.Frame(dash_recent_chart_frame)
        right_chart_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0), pady=0)
        self.dash_chart_frame = right_chart_frame  # Store dashboard chart frame for live updates
        self.dash_recent_chart_canvas = None
        self.draw_recent_3mo_chart(right_chart_frame)

        # Transactions Tab
        self.tab_transactions = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_transactions, text='Transactions')

        # --- Transactions Tab Content ---
        trx_main_frame = ttk.Frame(self.tab_transactions)
        trx_main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        trx_main_frame.columnconfigure(0, weight=1)
        trx_main_frame.columnconfigure(1, weight=1)
        trx_main_frame.rowconfigure(0, weight=1)

        # Left: Add Transaction (vertical stack)
        frm_add = ttk.LabelFrame(trx_main_frame, text='Add Transaction')
        frm_add.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=0)
        # Type
        ttk.Label(frm_add, text='Type:').pack(anchor='w', padx=5, pady=(10, 2))
        self.cmb_type = ttk.Combobox(frm_add, values=['Income', 'Expense'], state='readonly', width=15)
        self.cmb_type.set('Expense')
        self.cmb_type.pack(fill='x', padx=5, pady=2)
        self.cmb_type.bind('<<ComboboxSelected>>', lambda e: self.refresh_categories())
        # IMPORTANT: Make sure to call refresh_categories after setting up the combobox

        # Category
        ttk.Label(frm_add, text='Category:').pack(anchor='w', padx=5, pady=(8, 2))
        self.cmb_category = ttk.Combobox(frm_add, values=[], state='readonly', width=20)
        self.cmb_category.pack(fill='x', padx=5, pady=2)
        # Amount
        ttk.Label(frm_add, text='Amount:').pack(anchor='w', padx=5, pady=(8, 2))
        self.ent_amount = ttk.Entry(frm_add)
        self.ent_amount.pack(fill='x', padx=5, pady=2)
        # Date
        ttk.Label(frm_add, text='Date:').pack(anchor='w', padx=5, pady=(8, 2))
        if TKCALENDAR_AVAILABLE:
            self.ent_date = DateEntry(frm_add, width=15, date_pattern='yyyy-mm-dd')
            self.ent_date.set_date(datetime.now())
        else:
            self.ent_date = ttk.Entry(frm_add, width=15)
            self.ent_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.ent_date.pack(fill='x', padx=5, pady=2)
        # Description
        ttk.Label(frm_add, text='Description:').pack(anchor='w', padx=5, pady=(8, 2))
        self.ent_desc = ttk.Entry(frm_add)
        self.ent_desc.pack(fill='x', padx=5, pady=2)
        # Add Button
        ttk.Button(frm_add, text='Add', style='Accent.TButton', command=self.add_transaction).pack(pady=10)

        # Right: Charts (placeholder or actual chart logic)
        self.trx_chart_frame = ttk.LabelFrame(trx_main_frame, text='Charts')
        self.trx_chart_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 0), pady=0)
        self.trx_pie_canvas = None
        self.trx_bar_canvas = None
        # Draw charts in the right frame
        self.draw_trx_charts()

        # Transaction Summary Labels (below)
        summary_frame = ttk.Frame(self.tab_transactions)
        summary_frame.pack(fill='x', pady=(0, 5))
        self.lbl_trx_income = ttk.Label(summary_frame, text='Total Income:')
        self.lbl_trx_income.pack(side='left', padx=10)
        self.lbl_trx_expense = ttk.Label(summary_frame, text='Total Expense:')
        self.lbl_trx_expense.pack(side='left', padx=10)
        self.lbl_trx_balance = ttk.Label(summary_frame, text='Balance:')
        self.lbl_trx_balance.pack(side='left', padx=10)

        # Transactions Treeview (below)
        tree_frame = ttk.Frame(self.tab_transactions)
        tree_frame.pack(fill='both', expand=True, pady=10)
        columns = ('#', 'Type', 'Category', 'Amount', 'Date', 'Description')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill='both', expand=True)
        # Bind double-click to inline edit
        self.tree.bind('<Double-1>', self.edit_transaction)

        # Settings Tab
        self.tab_settings = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_settings, text='Settings')
        self.tabs.pack(fill='both', expand=True)
        # Settings tab content
        settings_frame = ttk.Frame(self.tab_settings)
        settings_frame.pack(pady=20, padx=20, fill='both', expand=True)

        # --- Currency Selection ---
        currency_frame = ttk.LabelFrame(settings_frame, text='Currency')
        currency_frame.pack(fill='x', pady=10)
        ttk.Label(currency_frame, text='Select Currency:').pack(side='left', padx=10, pady=10)
        self.settings_currency_var = tk.StringVar(value=self.currency)
        self.settings_currency_combo = ttk.Combobox(currency_frame, textvariable=self.settings_currency_var,
                                                    values=CURRENCIES, state='readonly', width=10)
        self.settings_currency_combo.pack(side='left', padx=10)
        ttk.Button(currency_frame, text='Update', style='Accent.TButton',
                   command=self.update_currency_from_settings).pack(side='left', padx=10)

        # --- Category Management ---
        cat_frame = ttk.LabelFrame(settings_frame, text='Manage Categories')
        cat_frame.pack(fill='both', expand=True, pady=10)
        self.settings_cat_tree = ttk.Treeview(cat_frame, columns=('id', 'name', 'type'), show='headings', height=8)
        for col in ['id', 'name', 'type']:
            self.settings_cat_tree.heading(col, text=col.capitalize())
            self.settings_cat_tree.column(col, width=100)
        self.settings_cat_tree.pack(fill='both', expand=True, pady=5)
        self.settings_cat_tree.bind('<Double-1>', self.inline_edit_category)
        btns_frame = ttk.Frame(cat_frame)
        btns_frame.pack(pady=5)
        ttk.Button(btns_frame, text='Add', style='Accent.TButton', command=self.settings_add_category).pack(side='left',
                                                                                                            padx=5)
        ttk.Button(btns_frame, text='Delete', style='Accent.TButton', command=self.settings_delete_category).pack(
            side='left', padx=5)

        # IMPORTANT: Call refresh_categories after UI is set up
        self.refresh_categories()
        self.settings_refresh_categories()

    def inline_edit_category(self, event):
        # Inline editing for categories in settings_cat_tree
        sel = self.settings_cat_tree.selection()
        if not sel:
            return
        item = self.settings_cat_tree.item(sel[0])['values']
        cid, name, ttype = item
        col = self.settings_cat_tree.identify_column(event.x)
        col_index = int(col.replace('#', '')) - 1

        # Only allow editing of name and type columns
        if col_index not in [1, 2]:
            return

        x, y, width, height = self.settings_cat_tree.bbox(sel[0], col)

        if col_index == 1:  # Name
            entry = ttk.Entry(self.settings_cat_tree)
            entry.insert(0, name)
            entry.place(x=x, y=y, width=width, height=height)
            entry.focus()

            def save_name(e=None):
                new_name = entry.get().strip()
                entry.destroy()
                if not new_name:
                    return
                try:
                    c = self.conn.cursor()
                    c.execute('UPDATE categories SET name=? WHERE id=?', (new_name, cid))
                    self.conn.commit()
                    vals = list(self.settings_cat_tree.item(sel[0])['values'])
                    vals[1] = new_name
                    self.settings_cat_tree.item(sel[0], values=vals)
                    self.refresh_all()
                except sqlite3.IntegrityError:
                    messagebox.showerror('Error', 'Category already exists.')

            entry.bind('<FocusOut>', save_name)
            entry.bind('<Return>', save_name)

        elif col_index == 2:  # Type
            cb = ttk.Combobox(self.settings_cat_tree, values=['Income', 'Expense'], state='readonly')
            cb.set(ttype)
            cb.place(x=x, y=y, width=width, height=height)
            cb.focus()

            def save_type(e=None):
                new_type = cb.get()
                cb.destroy()
                if new_type not in ['Income', 'Expense']:
                    return
                c = self.conn.cursor()
                c.execute('UPDATE categories SET type=? WHERE id=?', (new_type, cid))
                self.conn.commit()
                vals = list(self.settings_cat_tree.item(sel[0])['values'])
                vals[2] = new_type
                self.settings_cat_tree.item(sel[0], values=vals)
                self.refresh_all()

            cb.bind('<<ComboboxSelected>>', save_type)
            cb.bind('<FocusOut>', save_type)
            cb.bind('<Return>', save_type)

    def update_currency_from_settings(self):
        curr = self.settings_currency_var.get()
        if curr and curr in CURRENCIES:
            set_currency(curr)
            self.currency = curr
            self.refresh_all()
        else:
            messagebox.showerror('Invalid', 'Invalid or unsupported currency.')

    def settings_refresh_categories(self):
        for row in self.settings_cat_tree.get_children():
            self.settings_cat_tree.delete(row)
        c = self.conn.cursor()
        c.execute('SELECT id, name, type FROM categories ORDER BY type, name')
        for row in c.fetchall():
            self.settings_cat_tree.insert('', 'end', values=row)

    def settings_add_category(self):
        add_win = tk.Toplevel(self)
        add_win.title('Add Category')
        add_win.geometry('300x150')
        ttk.Label(add_win, text='Name:').pack(pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(add_win, textvariable=name_var)
        name_entry.pack(pady=5)
        ttk.Label(add_win, text='Type:').pack(pady=5)
        type_var = tk.StringVar(value='Expense')
        type_combo = ttk.Combobox(add_win, textvariable=type_var, values=['Income', 'Expense'], state='readonly')
        type_combo.pack(pady=5)

        def do_add():
            name = name_var.get().strip()
            ttype = type_var.get()
            if not name or ttype not in ['Income', 'Expense']:
                messagebox.showerror('Invalid', 'Invalid input.')
                return
            try:
                c = self.conn.cursor()
                c.execute('INSERT INTO categories (name, type) VALUES (?, ?)', (name, ttype))
                self.conn.commit()
                add_win.destroy()
                self.settings_refresh_categories()
                self.refresh_categories()
            except sqlite3.IntegrityError:
                messagebox.showerror('Error', 'Category already exists.')

        ttk.Button(add_win, text='Add', style='Accent.TButton', command=do_add).pack(pady=10)

    def settings_delete_category(self):
        sel = self.settings_cat_tree.selection()
        if not sel:
            return
        cid = self.settings_cat_tree.item(sel[0])['values'][0]
        if messagebox.askyesno('Delete', 'Delete this category? Transactions will remain.'):
            c = self.conn.cursor()
            c.execute('DELETE FROM categories WHERE id=?', (cid,))
            self.conn.commit()
            self.settings_refresh_categories()
            self.refresh_categories()

    def refresh_all(self):
        self.refresh_categories()
        self.refresh_overview()
        self.refresh_transactions()
        self.refresh_trx_summary()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        # Update summary cards and recent activity using selected date range
        c = self.conn.cursor()
        start, end = self.get_dashboard_date_range()
        # Income/Expense in range
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Income' AND date BETWEEN ? AND ?",
                  (str(start), str(end)))
        income = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense' AND date BETWEEN ? AND ?",
                  (str(start), str(end)))
        expense = c.fetchone()[0] or 0
        balance = income - expense
        if hasattr(self, 'dash_income_val'):
            self.dash_income_val['text'] = f'{self.currency} {income:.2f}'
            self.dash_expense_val['text'] = f'{self.currency} {expense:.2f}'
            self.dash_balance_val['text'] = f'{self.currency} {balance:.2f}'
            savings_rate = self.calculate_savings_rate(income, expense)
            self.dash_savings_val['text'] = f'{savings_rate:.1f}%' if savings_rate is not None else '—'
        # Net Worth Card
        if hasattr(self, 'dash_networth_label'):
            networth = income - expense
            self.dash_networth_label['text'] = f'{self.currency} {networth:.2f}'
        # Savings Goal Progress
        self.update_savings_goal_progress(income)
        # Recent activity: show last 6 transactions in range
        if hasattr(self, 'dash_recent'):
            for row in self.dash_recent.get_children():
                self.dash_recent.delete(row)
            c.execute(
                '''SELECT t.type, c.name, t.amount, t.date, t.description FROM transactions t JOIN categories c ON t.category_id=c.id WHERE t.date BETWEEN ? AND ? ORDER BY t.date DESC, t.id DESC LIMIT 6''',
                (str(start), str(end)))
            for row in c.fetchall():
                self.dash_recent.insert('', 'end', values=row)
        # Update charts
        if hasattr(self, 'draw_dashboard_charts'):
            self.draw_dashboard_charts()
        # Trends & Insights
        if hasattr(self, 'dash_trends_label'):
            # Compare this month vs last month expense
            import datetime
            today = datetime.date.today()
            # This month
            this_month_start = today.replace(day=1).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')
            c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense' AND date BETWEEN ? AND ?",
                      (this_month_start, today_str))
            this_month_exp = c.fetchone()[0] or 0
            # Last month
            first = today.replace(day=1)
            last_month_end = (first - datetime.timedelta(days=1))
            last_month_start = last_month_end.replace(day=1)
            last_month_start_str = last_month_start.strftime('%Y-%m-%d')
            last_month_end_str = last_month_end.strftime('%Y-%m-%d')
            c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense' AND date BETWEEN ? AND ?",
                      (last_month_start_str, last_month_end_str))
            last_month_exp = c.fetchone()[0] or 0
            if last_month_exp > 0:
                change = ((this_month_exp - last_month_exp) / last_month_exp) * 100
                if change > 0:
                    trend = f'Spending increased by {change:.1f}% compared to last month.'
                elif change < 0:
                    trend = f'Spending decreased by {abs(change):.1f}% compared to last month.'
                else:
                    trend = 'Spending is unchanged compared to last month.'
            else:
                trend = 'No spending data for last month.'
            self.dash_trends_label['text'] = trend

    def calculate_savings_rate(self, income, expense):
        try:
            if income == 0:
                return None
            savings = income - expense
            return (savings / income) * 100
        except Exception:
            return None

    def get_dashboard_date_range(self):
        import datetime
        range_val = self.dash_date_range.get() if hasattr(self, 'dash_date_range') else 'This Month'
        today = datetime.date.today()
        if range_val == 'This Month':
            start = today.replace(day=1)
            end = today
        elif range_val == 'Last Month':
            first = today.replace(day=1)
            last_month_end = first - datetime.timedelta(days=1)
            start = last_month_end.replace(day=1)
            end = last_month_end
        elif range_val == 'Last 3 Months':
            month = today.month - 2
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            start = today.replace(year=year, month=month, day=1)
            end = today
        elif range_val == 'This Year':
            start = today.replace(month=1, day=1)
            end = today
        elif range_val == 'Custom...':
            try:
                from datetime import datetime as dt
                start = dt.strptime(self.dash_custom_start.get(), '%Y-%m-%d').date()
                end = dt.strptime(self.dash_custom_end.get(), '%Y-%m-%d').date()
            except Exception:
                start = end = today
        else:
            start = today.replace(day=1)
            end = today
        return start, end

    def on_dashboard_range_change(self, event=None):
        val = self.dash_date_range.get()
        if val == 'Custom...':
            self.dash_custom_start.pack(side='left', padx=5)
            self.dash_custom_end.pack(side='left', padx=5)
        else:
            self.dash_custom_start.pack_forget()
            self.dash_custom_end.pack_forget()
        self.refresh_dashboard()

    def set_savings_goal(self):
        try:
            amt = float(self.dash_goal_amount.get())
            if amt <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror('Invalid Input', 'Please enter a valid positive number for the goal.')
            return
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('savings_goal', ?)", (str(amt),))
        self.conn.commit()
        self.load_savings_goal()
        self.refresh_dashboard()

    def load_savings_goal(self):
        c = self.conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='savings_goal'")
        res = c.fetchone()
        if res:
            try:
                amt = float(res[0])
                self.dash_goal_amount.delete(0, tk.END)
                self.dash_goal_amount.insert(0, str(amt))
                self.dash_goal = amt
            except Exception:
                self.dash_goal = None
        else:
            self.dash_goal = None
        self.update_savings_goal_progress()

    def update_savings_goal_progress(self, income=None):
        if not hasattr(self, 'dash_goal_progress'):
            return
        if not hasattr(self, 'dash_goal'):
            self.dash_goal = None
        if self.dash_goal is None:
            self.dash_goal_progress['value'] = 0
            self.dash_goal_status['text'] = 'No goal set.'
            return
        # Use current dashboard income if provided, else recalc
        if income is None:
            c = self.conn.cursor()
            start, end = self.get_dashboard_date_range()
            c.execute("SELECT SUM(amount) FROM transactions WHERE type='Income' AND date BETWEEN ? AND ?",
                      (str(start), str(end)))
            income = c.fetchone()[0] or 0
        progress = min(income / self.dash_goal, 1.0) if self.dash_goal > 0 else 0
        self.dash_goal_progress['value'] = progress * 100
        if progress >= 1.0:
            self.dash_goal_status['text'] = 'Goal achieved!'
        else:
            self.dash_goal_status['text'] = f'{progress * 100:.1f}% of goal'

    def draw_dashboard_charts(self):
        # Only show last 3 months spending chart in dashboard
        if hasattr(self, 'dash_chart_frame'):
            # Remove any previous chart widgets in the frame
            for child in self.dash_chart_frame.winfo_children():
                child.destroy()
            self.draw_recent_3mo_chart(self.dash_chart_frame)

    def draw_recent_3mo_chart(self, parent):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import calendar, datetime
        c = self.conn.cursor()
        # Get last 3 months (adaptive)
        today = datetime.date.today()
        months = []
        month_labels = []
        for i in range(2, -1, -1):
            m = (today.month - i - 1) % 12 + 1
            y = today.year if today.month - i > 0 else today.year - 1
            months.append((y, m))
            month_labels.append(f'{calendar.month_abbr[m]} {y}')
        # Query expenses for each month
        expenses = []
        for y, m in months:
            month_start = f'{y}-{m:02d}-01'
            if m == 12:
                next_month_start = f'{y + 1}-01-01'
            else:
                next_month_start = f'{y}-{m + 1:02d}-01'
            c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense' AND date >= ? AND date < ?",
                      (month_start, next_month_start))
            amt = c.fetchone()[0] or 0
            expenses.append(amt)
        fig = plt.Figure(figsize=(3.8, 2.8), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(month_labels, expenses, color='#e74c3c')
        ax.set_title('Spending (Last 3 Months)')
        ax.set_ylabel('Amount')
        for i, v in enumerate(expenses):
            ax.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=9)
        fig.tight_layout()
        if hasattr(self, 'dash_recent_chart_canvas') and self.dash_recent_chart_canvas:
            self.dash_recent_chart_canvas.get_tk_widget().destroy()
        self.dash_recent_chart_canvas = FigureCanvasTkAgg(fig, master=parent)
        self.dash_recent_chart_canvas.draw()
        self.dash_recent_chart_canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

    def draw_trx_charts(self):
        self._draw_charts(self.trx_chart_frame, is_dashboard=False)

    def _draw_charts(self, frame, is_dashboard):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import calendar
        # Remove old charts if present
        if not is_dashboard:
            if hasattr(self, 'trx_pie_canvas') and self.trx_pie_canvas:
                self.trx_pie_canvas.get_tk_widget().destroy()
            if hasattr(self, 'trx_bar_canvas') and self.trx_bar_canvas:
                self.trx_bar_canvas.get_tk_widget().destroy()
        # Only draw charts for transactions tab (not dashboard)
        if not is_dashboard:
            # Pie chart for expenses by category
            c = self.conn.cursor()
            c.execute("""
                SELECT c.name, SUM(t.amount) FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.type='Expense'
                GROUP BY c.name
            """)
            data = c.fetchall()
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]
            pie_fig = plt.Figure(figsize=(3.2, 3), dpi=100)
            pie_ax = pie_fig.add_subplot(111)
            if sizes:
                pie_ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            pie_ax.set_title('Expenses by Category')
            pie_canvas = FigureCanvasTkAgg(pie_fig, master=frame)
            pie_canvas.draw()
            pie_canvas.get_tk_widget().pack(side='left', padx=10, pady=10)
            # Bar chart for income/expense by month
            c.execute("""
                SELECT strftime('%m', date), type, SUM(amount) FROM transactions
                WHERE date >= date('now', '-11 months')
                GROUP BY strftime('%Y-%m', date), type
            """)
            rows = c.fetchall()
            months = [calendar.month_abbr[i + 1] for i in range(12)]
            income_vals = [0] * 12
            expense_vals = [0] * 12
            for row in rows:
                month_idx = int(row[0]) - 1
                if row[1] == 'Income':
                    income_vals[month_idx] += row[2]
                else:
                    expense_vals[month_idx] += row[2]
            bar_fig = plt.Figure(figsize=(5.5, 3), dpi=100)
            bar_ax = bar_fig.add_subplot(111)
            x = range(12)
            bar_ax.bar(x, income_vals, width=0.4, label='Income', color='#6cc24a')
            bar_ax.bar([i + 0.4 for i in x], expense_vals, width=0.4, label='Expense', color='#e74c3c')
            bar_ax.set_xticks([i + 0.2 for i in x])
            bar_ax.set_xticklabels(months, rotation=30)
            bar_ax.set_title('Income & Expense by Month')
            bar_ax.legend()
            bar_canvas = FigureCanvasTkAgg(bar_fig, master=frame)
            bar_canvas.draw()
            bar_canvas.get_tk_widget().pack(side='left', padx=10, pady=10)
            # Store references
            self.trx_pie_canvas = pie_canvas
            self.trx_bar_canvas = bar_canvas

    def refresh_categories(self):
        # Defensive: only update if widgets exist
        if not hasattr(self, 'cmb_type') or not hasattr(self, 'cmb_category'):
            return
        c = self.conn.cursor()
        ttype = self.cmb_type.get()
        c.execute('SELECT name FROM categories WHERE type=?', (ttype,))
        cats = [row[0] for row in c.fetchall()]
        self.cmb_category['values'] = cats
        if cats:
            self.cmb_category.set(cats[0])
        else:
            self.cmb_category.set('')
        print(f"Loaded {len(cats)} categories for type: {ttype}")  # Debug output

    def refresh_overview(self):
        c = self.conn.cursor()
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
        income = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
        expense = c.fetchone()[0] or 0
        balance = income - expense
        # --- Dashboard summary cards ---
        if hasattr(self, 'dash_income_val'):
            self.dash_income_val['text'] = f'{self.currency} {income:.2f}'
            self.dash_expense_val['text'] = f'{self.currency} {expense:.2f}'
            self.dash_balance_val['text'] = f'{self.currency} {balance:.2f}'
            savings_rate = self.calculate_savings_rate(income, expense)
            self.dash_savings_val['text'] = f'{savings_rate:.1f}%' if savings_rate is not None else '—'

    def refresh_transactions(self):
        if not hasattr(self, 'tree'):
            return
        # Store mapping of treeview item ID to DB transaction ID
        self.tree_id_to_dbid = {}
        for row in self.tree.get_children():
            self.tree.delete(row)
        c = self.conn.cursor()
        c.execute(
            '''SELECT t.id, t.type, c.name, t.amount, t.date, t.description FROM transactions t JOIN categories c ON t.category_id=c.id ORDER BY t.date DESC''')
        rows = c.fetchall()
        for idx, row in enumerate(rows, 1):
            item_id = self.tree.insert('', 'end', values=(idx, row[1], row[2], row[3], row[4], row[5]))
            self.tree_id_to_dbid[item_id] = row[0]
        # Update charts in transaction tab
        if hasattr(self, 'trx_chart_frame'):
            self._draw_charts(self.trx_chart_frame, is_dashboard=False)

    def refresh_trx_summary(self):
        # Defensive: only update if widgets exist
        if not (hasattr(self, 'lbl_trx_income') and hasattr(self, 'lbl_trx_expense') and hasattr(self,
                                                                                                 'lbl_trx_balance')):
            return
        c = self.conn.cursor()
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
        income = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
        expense = c.fetchone()[0] or 0
        balance = income - expense
        self.lbl_trx_income['text'] = f'Total Income: {self.currency} {income:.2f}'
        self.lbl_trx_expense['text'] = f'Total Expense: {self.currency} {expense:.2f}'
        self.lbl_trx_balance['text'] = f'Balance: {self.currency} {balance:.2f}'

    def add_transaction(self):
        ttype = self.cmb_type.get()
        cat = self.cmb_category.get()
        amt = self.ent_amount.get()
        date = self.ent_date.get()
        desc = self.ent_desc.get()
        try:
            amt = float(amt)
            datetime.strptime(date, '%Y-%m-%d')
        except:
            messagebox.showerror('Invalid Input', 'Please enter valid amount and date.')
            return
        c = self.conn.cursor()
        c.execute('SELECT id FROM categories WHERE name=? AND type=?', (cat, ttype))
        cat_id = c.fetchone()
        if not cat_id:
            messagebox.showerror('Category Error', 'Category not found.')
            return
        c.execute('''INSERT INTO transactions (amount, category_id, date, description, type) VALUES (?, ?, ?, ?, ?)''',
                  (amt, cat_id[0], date, desc, ttype))
        self.conn.commit()
        self.refresh_all()
        self.ent_amount.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)

    def edit_transaction(self, event):
        # Inline editing: double-click on any cell to edit all fields
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])['values']
        # Use DB ID from mapping
        dbid = self.tree_id_to_dbid.get(sel[0])
        if dbid is None:
            return
        ttype = item[1]
        cat = item[2]
        amt = item[3]
        date = item[4]
        desc = item[5]
        columns = ['#', 'Type', 'Category', 'Amount', 'Date', 'Description']
        if event:
            region = self.tree.identify('region', event.x, event.y)
            if region != 'cell':
                return
            col = self.tree.identify_column(event.x)
            col_index = int(col.replace('#', '')) - 1
            x, y, width, height = self.tree.bbox(sel[0], col)
            value = self.tree.item(sel[0])['values'][col_index]
            # Type (1): Combobox
            if col_index == 1:
                cb = ttk.Combobox(self.tree, values=['Income', 'Expense'], state='readonly')
                cb.set(ttype)
                cb.place(x=x, y=y, width=width, height=height)
                cb.focus_set()

                def save_type(event=None):
                    new_type = cb.get()
                    cb.destroy()
                    vals = list(self.tree.item(sel[0])['values'])
                    vals[col_index] = new_type
                    # Also update category to first available of new type
                    c = self.conn.cursor()
                    c.execute('SELECT name FROM categories WHERE type=?', (new_type,))
                    cats = [row[0] for row in c.fetchall()]
                    vals[2] = cats[0] if cats else ''
                    self.tree.item(sel[0], values=vals)
                    # Update DB
                    c.execute(
                        'UPDATE transactions SET type=?, category_id=(SELECT id FROM categories WHERE name=? AND type=?) WHERE id=?',
                        (new_type, vals[2], new_type, dbid))
                    self.conn.commit()
                    self.refresh_all()

                cb.bind('<<ComboboxSelected>>', save_type)
                cb.bind('<FocusOut>', save_type)
            # Category (2): Combobox
            elif col_index == 2:
                c = self.conn.cursor()
                c.execute('SELECT name FROM categories WHERE type=?', (ttype,))
                cats = [row[0] for row in c.fetchall()]
                cb = ttk.Combobox(self.tree, values=cats, state='readonly')
                cb.set(cat)
                cb.place(x=x, y=y, width=width, height=height)
                cb.focus_set()

                def save_cat(event=None):
                    new_cat = cb.get()
                    cb.destroy()
                    vals = list(self.tree.item(sel[0])['values'])
                    vals[col_index] = new_cat
                    self.tree.item(sel[0], values=vals)
                    c = self.conn.cursor()
                    c.execute(
                        'UPDATE transactions SET category_id=(SELECT id FROM categories WHERE name=? AND type=?) WHERE id=?',
                        (new_cat, ttype, dbid))
                    self.conn.commit()
                    self.refresh_all()

                cb.bind('<<ComboboxSelected>>', save_cat)
                cb.bind('<FocusOut>', save_cat)
            # Amount (3): Entry
            elif col_index == 3:
                entry = ttk.Entry(self.tree)
                entry.insert(0, amt)
                entry.place(x=x, y=y, width=width, height=height)
                entry.focus_set()

                def save_amt(event=None):
                    new_val = entry.get()
                    entry.destroy()
                    try:
                        new_amt = float(new_val)
                    except ValueError:
                        return
                    vals = list(self.tree.item(sel[0])['values'])
                    vals[col_index] = new_amt
                    self.tree.item(sel[0], values=vals)
                    c = self.conn.cursor()
                    c.execute('UPDATE transactions SET amount=? WHERE id=?', (new_amt, dbid))
                    self.conn.commit()
                    self.refresh_all()

                entry.bind('<FocusOut>', save_amt)
                entry.bind('<Return>', save_amt)
            # Date (4): Entry
            elif col_index == 4:
                entry = ttk.Entry(self.tree)
                entry.insert(0, date)
                entry.place(x=x, y=y, width=width, height=height)
                entry.focus_set()

                def save_date(event=None):
                    new_val = entry.get()
                    entry.destroy()
                    try:
                        datetime.strptime(new_val, '%Y-%m-%d')
                    except ValueError:
                        return
                    vals = list(self.tree.item(sel[0])['values'])
                    vals[col_index] = new_val
                    self.tree.item(sel[0], values=vals)
                    c = self.conn.cursor()
                    c.execute('UPDATE transactions SET date=? WHERE id=?', (new_val, dbid))
                    self.conn.commit()
                    self.refresh_all()

                entry.bind('<FocusOut>', save_date)
                entry.bind('<Return>', save_date)
            # Description (5): Entry
            elif col_index == 5:
                entry = ttk.Entry(self.tree)
                entry.insert(0, desc)
                entry.place(x=x, y=y, width=width, height=height)
                entry.focus_set()

                def save_desc(event=None):
                    new_val = entry.get()
                    entry.destroy()
                    vals = list(self.tree.item(sel[0])['values'])
                    vals[col_index] = new_val
                    self.tree.item(sel[0], values=vals)
                    c = self.conn.cursor()
                    c.execute('UPDATE transactions SET description=? WHERE id=?', (new_val, dbid))
                    self.conn.commit()
                    self.refresh_all()

                entry.bind('<FocusOut>', save_desc)
                entry.bind('<Return>', save_desc)


if __name__ == '__main__':
    # Delete existing database to avoid schema conflicts
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed existing {DB_FILE} to avoid schema conflicts")

    # Initialize with correct schema
    init_db()

    if not TKCALENDAR_AVAILABLE:
        messagebox.showwarning('Missing tkcalendar',
                               'For best date selection experience, please install tkcalendar: pip install tkcalendar')

    app = FinanceTrackerApp()
    app.mainloop()
