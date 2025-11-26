# Bubble Tea Shop Telegram Bot

## Overview
A bilingual (Thai/English) Telegram bot for managing sales at a bubble tea shop. The bot uses long polling (no webhooks) and stores all sales data in a local SQLite database.

## Features
- **Bilingual Interface**: All bot messages and buttons display in both Thai and English
- **New Sale Recording**: Step-by-step process to record drinks sales
- **Payment Methods**: Cash and QR payment options only
- **Sales Reports**: Today, Weekly, Monthly, and All-time reports with exact date ranges
- **Detailed Reports**: Click "Details" button on any report to see drink-by-drink breakdown
- **Admin Restrictions**: Only @dkokhel can access admin features and detailed reports
- **Complete Menu**: Full menu with 4 categories and multiple drink options
- **Database Storage**: All sales saved to SQLite with timestamps

## Menu Categories
1. **นม&ชา / Milk & Tea** - 13 drinks (Hot/Iced/Frappe)
2. **กาแฟ / Coffee** - 5 drinks (Hot/Iced/Frappe)
3. **อิตาเลียนโซดา / Italian Soda** - 12 drinks (Iced/Frappe only)
4. **อื่นๆ / Others** - 5 drinks (Iced/Frappe only)

## Technical Details
- **Language**: Python 3.11
- **Framework**: aiogram (v3.22.0)
- **Database**: SQLite (sales.db)
- **Polling**: Long polling via asyncio
- **Environment**: TELEGRAM_TOKEN stored in Replit Secrets

## Database Schema
Table: `sales`
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- datetime (TEXT) - ISO format
- drink_name (TEXT) - Bilingual name
- category (TEXT) - Bilingual category
- size (TEXT) - Hot/Iced/Frappe
- price (REAL) - In Thai Baht
- payment_type (TEXT) - cash/qr/other

## Running the Bot
The bot runs automatically via the "Telegram Bot" workflow. Click the Run button or use:
```bash
python main.py
```

## Bot Commands
- `/start` - Show main menu
- `/report` - Show today's sales report (with exact date)
- `/admin` - Show admin menu with all reports
- `/week` - Show current week's report (Monday to Sunday)
- `/month` - Show current month's report
- `/alltime` - Show all-time sales report

## Recent Changes
- 2025-11-26: Added "Details" button to all reports showing drink-by-drink breakdown
- 2025-11-26: Restricted admin features to @dkokhel only
- 2025-11-26: Changed payment methods to Cash and QR only
- 2025-11-26: Added admin menu with weekly, monthly, and all-time reports
- 2025-11-26: All reports now show explicit date ranges
- 2025-11-26: Updated to full bilingual menu with complete drink list
- 2025-11-26: Initial bot implementation with basic menu

## Reporting Features
All reports display in bilingual format (Thai/English) and include explicit date ranges:

### Today Report (`/report`)
Shows sales for current date with exact date displayed

### Weekly Report (`/week`)
Shows sales for current calendar week (Monday to Sunday) with date range

### Monthly Report (`/month`)
Shows sales for current month from 1st to current date with date range

### All-time Report (`/alltime`)
Shows all sales from earliest to latest with complete date range

### Admin Menu (`/admin`)
Provides quick access to all reports through inline keyboard buttons
- **Restricted Access**: Only visible to @dkokhel
- All admin commands return an error message for non-admin users

### Details Button
Every report includes a "📋 รายละเอียด / Details" button that shows:
- Complete breakdown by drink name
- Individual drink sales count and total revenue
- Sorted by highest revenue first
- Available for all report types (Today, Week, Month, All-time)
