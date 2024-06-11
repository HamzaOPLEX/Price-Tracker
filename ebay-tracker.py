import smtplib
import sqlite3
import time
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import requests
from prettytable import PrettyTable

# Database setup
conn = sqlite3.connect('ebay_products.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS products
             (id TEXT PRIMARY KEY, url TEXT, name TEXT, price TEXT, last_checked TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS settings
             (key TEXT PRIMARY KEY, value TEXT)''')
conn.commit()

# Set default check interval
DEFAULT_INTERVAL = 7200  # 2 hours in seconds
c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('check_interval', ?)", (DEFAULT_INTERVAL,))
conn.commit()

def send_email(subject, body, to_email):
    from_email = "your_email@gmail.com"
    from_password = "your_email_password"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def parse_product(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    def css(css_selector):
        element = soup.select_one(css_selector)
        return element.get_text(strip=True) if element else ""

    item = {}
    item["url"] = soup.select_one('link[rel="canonical"]')["href"] if soup.select_one('link[rel="canonical"]') else ""
    item["id"] = item["url"].split("/itm/")[1].split("?")[0] if item["url"] else ""
    item["price"] = css('.x-price-primary>span')
    item["name"] = css("h1 span")

    return item

# establish our request session with browser-like headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
})

def check_price(url):
    response = session.get(url)
    product = parse_product(response.text)

    c.execute("SELECT price FROM products WHERE id = ?", (product["id"],))
    row = c.fetchone()

    if row:
        old_price = row[0]
        if old_price != product["price"]:
            send_email("Price Changed!", f'The price of {product["name"]} has changed from {old_price} to {product["price"]}. URL: {product["url"]}', "recipient_email@gmail.com")
            c.execute("UPDATE products SET price = ?, last_checked = datetime('now') WHERE id = ?", (product["price"], product["id"]))
    else:
        c.execute("INSERT INTO products (id, url, name, price, last_checked) VALUES (?, ?, ?, ?, datetime('now'))", (product["id"], product["url"], product["name"], product["price"]))

    conn.commit()

def list_products():
    c.execute("SELECT id, url, price, last_checked FROM products")
    rows = c.fetchall()

    table = PrettyTable()
    table.field_names = ["ID", "URL", "Price", "Last Checked"]

    for row in rows:
        table.add_row(row)

    print(table)

def add_product(url):
    response = session.get(url)
    product = parse_product(response.text)
    c.execute("INSERT INTO products (id, url, name, price, last_checked) VALUES (?, ?, ?, ?, datetime('now'))", (product["id"], product["url"], product["name"], product["price"]))
    conn.commit()
    print("Product added successfully")

def edit_product(id, new_url):
    response = session.get(new_url)
    product = parse_product(response.text)
    c.execute("UPDATE products SET url = ?, name = ?, price = ?, last_checked = datetime('now') WHERE id = ?", (product["url"], product["name"], product["price"], id))
    conn.commit()
    print("Product updated successfully")

def set_interval(interval):
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('check_interval', ?)", (interval,))
    conn.commit()
    print(f"Check interval set to {interval} seconds")

def get_interval():
    c.execute("SELECT value FROM settings WHERE key = 'check_interval'")
    interval = c.fetchone()[0]
    return int(interval)

def monitor_prices():
    while True:
        c.execute("SELECT url FROM products")
        urls = c.fetchall()
        for url in urls:
            check_price(url[0])
        time.sleep(get_interval())

def check_product_price(id, update=False):
    c.execute("SELECT url, price FROM products WHERE id = ?", (id,))
    row = c.fetchone()
    if row:
        url, old_price = row
        response = session.get(url)
        product = parse_product(response.text)
        new_price = product["price"]
        if old_price != new_price:
            print(f"Price changed for product {id}: {old_price} -> {new_price}")
            if update:
                c.execute("UPDATE products SET price = ?, last_checked = datetime('now') WHERE id = ?", (new_price, id))
                conn.commit()
                print(f"Updated price in the database for product {id}.")
        else:
            print(f"No price change for product {id}. Current price: {new_price}")
    else:
        print(f"No product found with ID: {id}")

def main():
    parser = argparse.ArgumentParser(description='Ebay Price Tracker')
    subparsers = parser.add_subparsers(dest='command')

    list_parser = subparsers.add_parser('list', help='List all products')

    add_parser = subparsers.add_parser('add', help='Add a new product')
    add_parser.add_argument('url', type=str, help='URL of the eBay product')

    edit_parser = subparsers.add_parser('edit', help='Edit an existing product')
    edit_parser.add_argument('id', type=str, help='ID of the product to edit')
    edit_parser.add_argument('new_url', type=str, help='New URL of the eBay product')

    interval_parser = subparsers.add_parser('interval', help='Set check interval')
    interval_parser.add_argument('seconds', type=int, help='Interval in seconds')

    monitor_parser = subparsers.add_parser('monitor', help='Start monitoring prices')

    check_parser = subparsers.add_parser('check', help='Check the price of a specific product')
    check_parser.add_argument('id', type=str, help='ID of the product to check')
    check_parser.add_argument('--update', action='store_true', help='Update the price in the database if different')

    args = parser.parse_args()

    if args.command == 'list':
        list_products()
    elif args.command == 'add':
        add_product(args.url)
    elif args.command == 'edit':
        edit_product(args.id, args.new_url)
    elif args.command == 'interval':
        set_interval(args.seconds)
    elif args.command == 'monitor':
        monitor_prices()
    elif args.command == 'check':
        check_product_price(args.id, args.update)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
