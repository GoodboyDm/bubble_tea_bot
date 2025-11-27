"""
Telegram Bot for Bubble Tea Shop
==================================
This bot helps manage sales for a small bubble tea shop.

SETUP INSTRUCTIONS:
1. Set your Telegram bot token:
   - Go to the "Secrets" tab in Replit (lock icon on the left sidebar)
   - Add a new secret with key: TELEGRAM_TOKEN
   - Value: your bot token from @BotFather

2. Run the bot:
   - Click the "Run" button at the top of Replit
   - Or run "python main.py" in the Shell

The bot will start using long polling (no webhooks needed).
"""

import os
import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================================================================
# ADMIN HELPER
# ============================================================================
def is_admin_user(user: types.User) -> bool:
    """Check if user is an admin"""
    admins = {"dkokhel", "nangsihalath"}
    return (user.username or "").lower() in admins

# ============================================================================
# MENU CONFIGURATION - BILINGUAL (Thai / English)
# ============================================================================
MENU = {
    "นม&ชา / Milk & Tea": {
        "ชาเย็น / Thai Tea": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "ชาเขียว / Green Tea": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "ชาเขียวโออิชิ / Oishi Green Tea": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "ชาดำ / Black Tea": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "ชามะนาว / Lemon Tea": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "ชาเขียวมะนาว / Green Tea Lemon": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "ชานมใต้หวัน / Taiwan Milk Tea": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "โกโก้ / Cocoa": {"Hot": 30, "Iced": 35, "Frappe": 45},
        "โอวัลติน / Ovaltine Milk": {"Hot": 30, "Iced": 35, "Frappe": 45},
        "นมสด / Fresh Milk": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "นมชมพู / Pink Milk": {"Hot": 25, "Iced": 35, "Frappe": 45},
        "เผือกหอม / Taro Milk Tea": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "แคนตาลูป / Cantaloupe Milk": {"Hot": 25, "Iced": 30, "Frappe": 45}
    },
    "กาแฟ / Coffee": {
        "เนสกาแฟ / Nescafé": {"Hot": 25, "Iced": 35, "Frappe": 45},
        "กาแฟโบราณ / Traditional Coffee": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "โอเลี้ยง / Thai Black Coffee": {"Hot": 25, "Iced": 30, "Frappe": 45},
        "โอเลี้ยงยกล้อ / Iced Coffee Mix": {"Hot": 25, "Iced": 35, "Frappe": 45},
        "มอคค่า / Mocha": {"Hot": 25, "Iced": 35, "Frappe": 45}
    },
    "อิตาเลียนโซดา / Italian Soda": {
        "บลูฮาวายโซดา / Blue Hawaii Soda": {"Iced": 30, "Frappe": 45},
        "บลูเบอร์รี่โซดา / Blueberry Soda": {"Iced": 30, "Frappe": 45},
        "สตรอเบอร์รี่โซดา / Strawberry Soda": {"Iced": 30, "Frappe": 45},
        "มะม่วงโซดา / Mango Soda": {"Iced": 30, "Frappe": 45},   # <-- добавили сюда
        "ลิ้นจี่โซดา / Lychee Soda": {"Iced": 30, "Frappe": 45},
        "สับปะรด / Pineapple Soda": {"Iced": 30, "Frappe": 45},
        "องุ่นโซดา / Grape Soda": {"Iced": 30, "Frappe": 45},
        "แอปเปิ้ลเขียวโซดา / Green Apple Soda": {"Iced": 30, "Frappe": 45},
        "กีวี่โซดา / Kiwi Soda": {"Iced": 30, "Frappe": 45},
        "เสาวรสโซดา / Passion Fruit Soda": {"Iced": 30, "Frappe": 45},
        "เขียวโซดา / Green Syrup Soda": {"Iced": 30, "Frappe": 45},
        "น้ำผึ้งมะนาวโซดา / Honey Lemon Soda": {"Iced": 35, "Frappe": 45},
        "บ้วยโซดา / Plum Soda": {"Iced": 30, "Frappe": 45}
    },
    "อื่นๆ / Others": {
        "นมสดคาราเมล / Caramel Milk": {"Iced": 35, "Frappe": 45},
        "นมสดบราวชูก้า / Brown Sugar Milk": {"Iced": 35, "Frappe": 45},
        "ชากาแฟ / Coffee Tea": {"Iced": 35, "Frappe": 45},
        "ชาโกโก้ / Cocoa Milk Tea": {"Iced": 35, "Frappe": 45},
        "เฉาก๊วยนมสด / Grass Jelly Milk": {"Iced": 35, "Frappe": 45}
    },
    "ท็อปปิ้ง / Toppings": {
        "คาราเมล / Caramel": {"Add": 5},
        "บราวน์ชูการ์ / Brown Sugar": {"Add": 5},
        "เพิ่มไข่มุก / Extra Black Pearls": {"Add": 5},
        "เพิ่มบุก / Extra Fruit Jelly": {"Add": 10},
        "เพิ่มปั่น / Extra Frappe Scoop": {"Add": 10},
        "ครีมชีส / Cream Cheese": {"Add": 15},
        "วิปปิ้ง / Whipping Cream": {"Add": 15},
        "ฟรุตสลัด วุ้น / Fruit Salad Jelly": {"Add": 10},
        "บ้วยสามรส / Three-Flavor Plum": {"Add": 20},
        "มันหนึบ / Chewy Sweet Balls": {"Add": 30},
        "ถุงกระดาษ / Paper Bag": {"Add": 40},
        "แก้วถัง / Big Bucket Cup": {"Add": 40}
    }
}

# ============================================================================
# DATABASE SETUP
# ============================================================================
def init_database():
    """Initialize SQLite database and create sales table if not exists."""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            drink_name TEXT NOT NULL,
            category TEXT NOT NULL,
            size TEXT NOT NULL,
            price REAL NOT NULL,
            payment_type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def save_sale(drink_name, category, size, price, payment_type):
    """Save a sale record to the database."""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO sales (datetime, drink_name, category, size, price, payment_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (now, drink_name, category, size, price, payment_type))
    conn.commit()
    conn.close()

def get_today_report():
    """Get today's sales report with date."""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
        SELECT COUNT(*), SUM(price)
        FROM sales
        WHERE datetime LIKE ?
    ''', (f"{today}%",))
    result = cursor.fetchone()
    conn.close()
    
    count = result[0] if result[0] else 0
    total = result[1] if result[1] else 0
    return today, count, total

def get_week_report():
    """Get current week's sales report (Monday to Sunday)."""
    from datetime import timedelta
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    start_date = monday.strftime("%Y-%m-%d")
    end_date = sunday.strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT COUNT(*), SUM(price)
        FROM sales
        WHERE datetime >= ? AND datetime <= ?
    ''', (f"{start_date} 00:00:00", f"{end_date} 23:59:59"))
    result = cursor.fetchone()
    conn.close()
    
    count = result[0] if result[0] else 0
    total = result[1] if result[1] else 0
    return start_date, end_date, count, total

def get_month_report():
    """Get current month's sales report."""
    from datetime import timedelta
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    today = datetime.now()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT COUNT(*), SUM(price)
        FROM sales
        WHERE datetime >= ? AND datetime <= ?
    ''', (f"{start_date} 00:00:00", f"{end_date} 23:59:59"))
    result = cursor.fetchone()
    conn.close()
    
    count = result[0] if result[0] else 0
    total = result[1] if result[1] else 0
    return start_date, end_date, count, total

def get_alltime_report():
    """Get all-time sales report with date range."""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*), SUM(price), MIN(datetime), MAX(datetime)
        FROM sales
    ''')
    result = cursor.fetchone()
    conn.close()
    
    count = result[0] if result[0] else 0
    total = result[1] if result[1] else 0
    
    if result[2] and result[3]:
        start_date = result[2][:10]
        end_date = result[3][:10]
    else:
        start_date = "N/A"
        end_date = "N/A"
    
    return start_date, end_date, count, total

def get_sales_details(start_datetime: str, end_datetime: str):
    """Get sales breakdown by drink for a given date range."""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT drink_name, COUNT(*), SUM(price)
        FROM sales
        WHERE datetime >= ? AND datetime <= ?
        GROUP BY drink_name
        ORDER BY SUM(price) DESC
    ''', (start_datetime, end_datetime))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

# ============================================================================
# USER SESSION STORAGE
# ============================================================================
# Simple in-memory storage for user sale sessions
user_sessions = {}

def get_session(user_id):
    """Get or create a session for a user."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    return user_sessions[user_id]

def clear_session(user_id):
    """Clear a user's session."""
    if user_id in user_sessions:
        user_sessions[user_id] = {}

# ============================================================================
# KEYBOARD BUILDERS
# ============================================================================
def get_main_keyboard(is_admin: bool):
    """Create the main menu keyboard."""
    rows = [
        [InlineKeyboardButton(text="🆕 ขายใหม่ / New sale", callback_data="new_sale")],
        [InlineKeyboardButton(text="📊 รายงานวันนี้ / Today report", callback_data="today_report")]
    ]
    if is_admin:
        rows.append([InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_admin_keyboard():
    """Create the admin menu keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 รายงานวันนี้ / Today Report", callback_data="today_report")],
        [InlineKeyboardButton(text="📆 รายงานรายสัปดาห์ / Weekly Report", callback_data="week_report")],
        [InlineKeyboardButton(text="📅 รายงานประจำเดือน / Monthly Report", callback_data="month_report")],
        [InlineKeyboardButton(text="🗂 รายงานทั้งหมด / All-time Report", callback_data="alltime_report")],
        [InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="back_to_main")]
    ])
    return keyboard

def get_category_keyboard():
    """Create keyboard for category selection."""
    buttons = []
    categories = list(MENU.keys())
    for idx, category in enumerate(categories):
        buttons.append([
            InlineKeyboardButton(
                text=category,
                callback_data=f"cat:{idx}"   # короткий ID
            )
        ])
    buttons.append([InlineKeyboardButton(text="❌ ยกเลิก / Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_drink_keyboard(category):
    """Create keyboard for drink selection within a category."""
    buttons = []
    if category in MENU:
        drinks = list(MENU[category].keys())
        for idx, drink in enumerate(drinks):
            buttons.append([
                InlineKeyboardButton(
                    text=drink,
                    callback_data=f"drink:{idx}"   # короткий ID
                )
            ])
    buttons.append([InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="back_to_category")])
    buttons.append([InlineKeyboardButton(text="❌ ยกเลิก / Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_size_keyboard(category, drink):
    """Create keyboard for size selection."""
    buttons = []
    if category in MENU and drink in MENU[category]:
        sizes = list(MENU[category][drink].keys())
        for idx, size in enumerate(sizes):
            buttons.append([
                InlineKeyboardButton(
                    text=size,
                    callback_data=f"size:{idx}"   # короткий ID
                )
            ])
    buttons.append([InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="back_to_drink")])
    buttons.append([InlineKeyboardButton(text="❌ ยกเลิก / Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_keyboard():
    """Create keyboard for payment type selection."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 เงินสด / Cash", callback_data="pay:cash")],
        [InlineKeyboardButton(text="📱 คิวอาร์ / QR", callback_data="pay:qr")],
        [InlineKeyboardButton(text="❌ ยกเลิก / Cancel", callback_data="cancel")]
    ])
    return keyboard

# ============================================================================
# BOT HANDLERS
# ============================================================================

async def cmd_start(message: types.Message):
    """Handle /start command."""
    welcome_text = (
    "🧋 ยินดีต้อนรับสู่ร้าน Cameron Pattaya!\n"
    "🧋 Welcome to Cameron Pattaya!\n\n"
    "ฉันจะช่วยคุณจัดการยอดขาย\n"
    "I'll help you manage your sales.\n\n"
    "เลือกตัวเลือกด้านล่าง:\n"
    "Choose an option below:"
)
    admin = is_admin_user(message.from_user)
    await message.answer(welcome_text, reply_markup=get_main_keyboard(admin))

async def cmd_report(message: types.Message):
    """Handle /report command (today)."""
    today, count, total = get_today_report()
    report_text = (
        f"📊 รายงานวันนี้ / Today report\n"
        f"วันที่: {today} / Date: {today}\n\n"
        f"ยอดขาย: {count} แก้ว / {count} cups\n"
        f"ยอดรวม: {total:,.2f} บาท / {total:,.2f} THB"
    )
    admin = is_admin_user(message.from_user)
    
    # Add Details button
    keyboard_rows = []
    keyboard_rows.append([InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:today")])
    if admin:
        keyboard_rows.append([InlineKeyboardButton(text="🆕 ขายใหม่ / New sale", callback_data="new_sale")])
        keyboard_rows.append([InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")])
    else:
        keyboard_rows.append([InlineKeyboardButton(text="🆕 ขายใหม่ / New sale", callback_data="new_sale")])
    
    await message.answer(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))

async def cmd_week(message: types.Message):
    """Handle /week command."""
    if not is_admin_user(message.from_user):
        await message.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only")
        return
    
    start_date, end_date, count, total = get_week_report()
    report_text = (
        f"📆 รายงานรายสัปดาห์ / Weekly report\n"
        f"ช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
        f"ยอดขาย: {count} แก้ว / {count} cups\n"
        f"ยอดรวม: {total:,.2f} บาท / {total:,.2f} THB"
    )
    
    # Add Details button
    keyboard_rows = list(get_admin_keyboard().inline_keyboard)
    keyboard_rows.insert(0, [InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:week")])
    
    await message.answer(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))

async def cmd_month(message: types.Message):
    """Handle /month command."""
    if not is_admin_user(message.from_user):
        await message.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only")
        return
    
    start_date, end_date, count, total = get_month_report()
    report_text = (
        f"📅 รายงานประจำเดือนนี้ / This month report\n"
        f"ช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
        f"ยอดขาย: {count} แก้ว / {count} cups\n"
        f"ยอดรวม: {total:,.2f} บาท / {total:,.2f} THB"
    )
    
    # Add Details button
    keyboard_rows = list(get_admin_keyboard().inline_keyboard)
    keyboard_rows.insert(0, [InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:month")])
    
    await message.answer(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))

async def cmd_alltime(message: types.Message):
    """Handle /alltime command."""
    if not is_admin_user(message.from_user):
        await message.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only")
        return
    
    start_date, end_date, count, total = get_alltime_report()
    report_text = (
        f"🗂 รายงานทั้งหมด / All-time report\n"
        f"ช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
        f"ยอดขายรวม: {count} แก้ว / {count} cups\n"
        f"ยอดรวมทั้งหมด: {total:,.2f} บาท / {total:,.2f} THB"
    )
    
    # Add Details button
    keyboard_rows = list(get_admin_keyboard().inline_keyboard)
    keyboard_rows.insert(0, [InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:alltime")])
    
    await message.answer(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))

async def cmd_admin(message: types.Message):
    """Handle /admin command."""
    if not is_admin_user(message.from_user):
        await message.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only")
        return
    
    admin_text = (
        "👤 เมนูแอดมิน / Admin Menu\n\n"
        "เลือกประเภทรายงาน:\n"
        "Choose report type:"
    )
    await message.answer(admin_text, reply_markup=get_admin_keyboard())

async def callback_handler(callback: types.CallbackQuery):
    """Handle all inline keyboard callbacks."""
    user_id = callback.from_user.id
    data = callback.data
    session = get_session(user_id)
    
    # ========== MAIN MENU ==========
    if data == "new_sale":
        clear_session(user_id)
        await callback.message.edit_text(
            "🆕 ขายใหม่ / New Sale\n\nขั้นที่ 1: เลือกหมวดหมู่\nStep 1: Choose category",
            reply_markup=get_category_keyboard()
        )
        await callback.answer()
        return
    
    if data == "today_report":
        today, count, total = get_today_report()
        report_text = (
            f"📊 รายงานวันนี้ / Today report\n"
            f"วันที่: {today} / Date: {today}\n\n"
            f"ยอดขาย: {count} แก้ว / {count} cups\n"
            f"ยอดรวม: {total:,.2f} บาท / {total:,.2f} THB"
        )
        admin = is_admin_user(callback.from_user)
        
        # Add Details button
        keyboard_rows = []
        keyboard_rows.append([InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:today")])
        if admin:
            keyboard_rows.append([InlineKeyboardButton(text="🆕 ขายใหม่ / New sale", callback_data="new_sale")])
            keyboard_rows.append([InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")])
        else:
            keyboard_rows.append([InlineKeyboardButton(text="🆕 ขายใหม่ / New sale", callback_data="new_sale")])
        
        await callback.message.edit_text(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    if data == "week_report":
        if not is_admin_user(callback.from_user):
            await callback.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only", show_alert=True)
            return
        
        start_date, end_date, count, total = get_week_report()
        report_text = (
            f"📆 รายงานรายสัปดาห์ / Weekly report\n"
            f"ช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
            f"ยอดขาย: {count} แก้ว / {count} cups\n"
            f"ยอดรวม: {total:,.2f} บาท / {total:,.2f} THB"
        )
        
        # Add Details button
        keyboard_rows = list(get_admin_keyboard().inline_keyboard)
        keyboard_rows.insert(0, [InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:week")])
        
        await callback.message.edit_text(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    if data == "month_report":
        if not is_admin_user(callback.from_user):
            await callback.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only", show_alert=True)
            return
        
        start_date, end_date, count, total = get_month_report()
        report_text = (
            f"📅 รายงานประจำเดือนนี้ / This month report\n"
            f"ช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
            f"ยอดขาย: {count} แก้ว / {count} cups\n"
            f"ยอดรวม: {total:,.2f} บาท / {total:,.2f} THB"
        )
        
        # Add Details button
        keyboard_rows = list(get_admin_keyboard().inline_keyboard)
        keyboard_rows.insert(0, [InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:month")])
        
        await callback.message.edit_text(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    if data == "alltime_report":
        if not is_admin_user(callback.from_user):
            await callback.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only", show_alert=True)
            return
        
        start_date, end_date, count, total = get_alltime_report()
        report_text = (
            f"🗂 รายงานทั้งหมด / All-time report\n"
            f"ช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
            f"ยอดขายรวม: {count} แก้ว / {count} cups\n"
            f"ยอดรวมทั้งหมด: {total:,.2f} บาท / {total:,.2f} THB"
        )
        
        # Add Details button
        keyboard_rows = list(get_admin_keyboard().inline_keyboard)
        keyboard_rows.insert(0, [InlineKeyboardButton(text="📋 รายละเอียด / Details", callback_data="details:alltime")])
        
        await callback.message.edit_text(report_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    if data == "admin_menu":
        if not is_admin_user(callback.from_user):
            await callback.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only", show_alert=True)
            return
        
        admin_text = (
            "👤 เมนูแอดมิน / Admin Menu\n\n"
            "เลือกประเภทรายงาน:\n"
            "Choose report type:"
        )
        await callback.message.edit_text(admin_text, reply_markup=get_admin_keyboard())
        await callback.answer()
        return
    
    if data == "back_to_main":
        welcome_text = (
            "🧋 ยินดีต้อนรับสู่บอทร้านชานมไข่มุก!\n"
            "🧋 Welcome to Bubble Tea Shop Bot!\n\n"
            "ฉันจะช่วยคุณจัดการยอดขาย\n"
            "I'll help you manage your sales.\n\n"
            "เลือกตัวเลือกด้านล่าง:\n"
            "Choose an option below:"
        )
        admin = is_admin_user(callback.from_user)
        await callback.message.edit_text(welcome_text, reply_markup=get_main_keyboard(admin))
        await callback.answer()
        return
    
    if data == "cancel":
        clear_session(user_id)
        admin = is_admin_user(callback.from_user)
        await callback.message.edit_text(
            "❌ ยกเลิกแล้ว เลือกตัวเลือก:\n❌ Cancelled. Choose an option:",
            reply_markup=get_main_keyboard(admin)
        )
        await callback.answer()
        return
    
    # ========== DETAILS REPORTS ==========
    if data == "details:today":
        today, _, _ = get_today_report()
        start_datetime = f"{today} 00:00:00"
        end_datetime = f"{today} 23:59:59"
        details = get_sales_details(start_datetime, end_datetime)
        
        detail_text = f"📋 รายละเอียดยอดขายวันนี้ / Today sales details\nวันที่: {today} / Date: {today}\n\n"
        
        if details:
            for drink_name, count, total in details:
                detail_text += f"{drink_name}: {count} แก้ว / {count} cups – {total:,.2f} บาท / {total:,.2f} THB\n"
        else:
            detail_text += "ไม่มีข้อมูลการขาย / No sales data"
        
        admin = is_admin_user(callback.from_user)
        keyboard_rows = []
        keyboard_rows.append([InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="today_report")])
        if admin:
            keyboard_rows.append([InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")])
        
        await callback.message.edit_text(detail_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    if data == "details:week":
        if not is_admin_user(callback.from_user):
            await callback.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only", show_alert=True)
            return
        
        start_date, end_date, _, _ = get_week_report()
        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"
        details = get_sales_details(start_datetime, end_datetime)
        
        detail_text = f"📆 รายละเอียดรายสัปดาห์ / Weekly sales details\nช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
        
        if details:
            for drink_name, count, total in details:
                detail_text += f"{drink_name}: {count} แก้ว / {count} cups – {total:,.2f} บาท / {total:,.2f} THB\n"
        else:
            detail_text += "ไม่มีข้อมูลการขาย / No sales data"
        
        keyboard_rows = [
            [InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="week_report")],
            [InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")]
        ]
        
        await callback.message.edit_text(detail_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    if data == "details:month":
        if not is_admin_user(callback.from_user):
            await callback.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only", show_alert=True)
            return
        
        start_date, end_date, _, _ = get_month_report()
        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"
        details = get_sales_details(start_datetime, end_datetime)
        
        detail_text = f"📅 รายละเอียดประจำเดือน / Monthly sales details\nช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
        
        if details:
            for drink_name, count, total in details:
                detail_text += f"{drink_name}: {count} แก้ว / {count} cups – {total:,.2f} บาท / {total:,.2f} THB\n"
        else:
            detail_text += "ไม่มีข้อมูลการขาย / No sales data"
        
        keyboard_rows = [
            [InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="month_report")],
            [InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")]
        ]
        
        await callback.message.edit_text(detail_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    if data == "details:alltime":
        if not is_admin_user(callback.from_user):
            await callback.answer("คำสั่งนี้สำหรับแอดมินเท่านั้น / This command is for admins only", show_alert=True)
            return
        
        start_date, end_date, _, _ = get_alltime_report()
        
        if start_date == "N/A":
            detail_text = "ไม่มีข้อมูลการขาย / No sales data available"
            keyboard_rows = [
                [InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="alltime_report")],
                [InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")]
            ]
            await callback.message.edit_text(detail_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
            await callback.answer()
            return
        
        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"
        details = get_sales_details(start_datetime, end_datetime)
        
        detail_text = f"🗂 รายละเอียดทั้งหมด / All-time sales details\nช่วงวันที่: {start_date} ถึง {end_date} / Date range: {start_date} to {end_date}\n\n"
        
        if details:
            for drink_name, count, total in details:
                detail_text += f"{drink_name}: {count} แก้ว / {count} cups – {total:,.2f} บาท / {total:,.2f} THB\n"
        else:
            detail_text += "ไม่มีข้อมูลการขาย / No sales data"
        
        keyboard_rows = [
            [InlineKeyboardButton(text="🔙 กลับ / Back", callback_data="alltime_report")],
            [InlineKeyboardButton(text="👤 แอดมิน / Admin", callback_data="admin_menu")]
        ]
        
        await callback.message.edit_text(detail_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
        await callback.answer()
        return
    
    # ========== CATEGORY SELECTION ==========
    if data.startswith("cat:"):
        idx = int(data.split(":", 1)[1])
        categories = list(MENU.keys())
        category = categories[idx]
        session['category'] = category
        await callback.message.edit_text(
            f"🆕 ขายใหม่ / New Sale\n\nหมวดหมู่ / Category: {category}\n\nขั้นที่ 2: เลือกเครื่องดื่ม\nStep 2: Choose drink:",
            reply_markup=get_drink_keyboard(category)
        )
        await callback.answer()
        return
    
    # ========== DRINK SELECTION ==========
    if data.startswith("drink:"):
        drink_idx = int(data.split(":", 1)[1])
        category = session.get('category')
        drinks = list(MENU[category].keys())
        drink = drinks[drink_idx]
        session['drink'] = drink
        await callback.message.edit_text(
            f"🆕 ขายใหม่ / New Sale\n\nหมวดหมู่ / Category: {category}\nเครื่องดื่ม / Drink: {drink}\n\nขั้นที่ 3: เลือกขนาด\nStep 3: Choose size:",
            reply_markup=get_size_keyboard(category, drink)
        )
        await callback.answer()
        return
    
    # ========== SIZE SELECTION ==========
    if data.startswith("size:"):
        size_idx = int(data.split(":", 1)[1])
        category = session.get('category')
        drink = session.get('drink')

        sizes = list(MENU[category][drink].keys())
        size = sizes[size_idx]

        session['size'] = size
        price = MENU[category][drink][size]
        session['price'] = price

        await callback.message.edit_text(
            f"🆕 ขายใหม่ / New Sale\n\n"
            f"หมวดหมู่ / Category: {category}\n"
            f"เครื่องดื่ม / Drink: {drink}\n"
            f"ขนาด / Size: {size}\n"
            f"ราคา / Price: {price} บาท / THB\n\n"
            f"ขั้นที่ 4: เลือกวิธีชำระเงิน\n"
            f"Step 4: Choose payment type:",
            reply_markup=get_payment_keyboard()
        )
        await callback.answer()
        return
    
    # ========== PAYMENT SELECTION ==========
    if data.startswith("pay:"):
        payment_type = data.split(":", 1)[1]

        category = session.get('category')
        drink = session.get('drink')
        size = session.get('size')
        price = session.get('price')

        # Save to database
        save_sale(drink, category, size, price, payment_type)

        # Clear session
        clear_session(user_id)

        # Определяем, админ ли пользователь
        admin = is_admin_user(callback.from_user)

        # Send confirmation
        await callback.message.edit_text(
            f"✅ บันทึกการขายแล้ว!\n✅ Sale saved!\n\n"
            f"เครื่องดื่ม / Drink: {drink}\n"
            f"ขนาด / Size: {size}\n"
            f"ยอดเงิน / Amount: {price} บาท / THB\n"
            f"ชำระโดย / Payment: {payment_type}",
            reply_markup=get_main_keyboard(admin)
        )
        await callback.answer("✅ บันทึกแล้ว / Saved!")
        return
    
    # ========== NAVIGATION ==========
    if data == "back_to_category":
        await callback.message.edit_text(
            "🆕 ขายใหม่ / New Sale\n\nขั้นที่ 1: เลือกหมวดหมู่\nStep 1: Choose category:",
            reply_markup=get_category_keyboard()
        )
        await callback.answer()
        return
    
    if data == "back_to_drink":
        category = session.get('category')
        await callback.message.edit_text(
            f"🆕 ขายใหม่ / New Sale\n\nหมวดหมู่ / Category: {category}\n\nขั้นที่ 2: เลือกเครื่องดื่ม\nStep 2: Choose drink:",
            reply_markup=get_drink_keyboard(category)
        )
        await callback.answer()
        return

# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """Main function to run the bot."""
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ ERROR: TELEGRAM_TOKEN environment variable not set!")
        print("\nPlease set your bot token:")
        print("1. Go to the 'Secrets' tab in Replit (lock icon)")
        print("2. Add a new secret:")
        print("   Key: TELEGRAM_TOKEN")
        print("   Value: your bot token from @BotFather")
        return
    
    # Initialize database
    init_database()
    
    # Create bot and dispatcher
    bot = Bot(token=token)
    dp = Dispatcher()
    
    # Register handlers
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_report, Command("report"))
    dp.message.register(cmd_week, Command("week"))
    dp.message.register(cmd_month, Command("month"))
    dp.message.register(cmd_alltime, Command("alltime"))
    dp.message.register(cmd_admin, Command("admin"))
    dp.callback_query.register(callback_handler)
    
    print("🚀 Bot started! Press Ctrl+C to stop.")
    print("📱 Go to your Telegram bot and type /start")
    
    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
