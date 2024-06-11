
# eBay Price Tracker

This script monitors the prices of products on eBay, stores the data in an SQLite database, and sends email notifications if the prices change. It includes a command-line interface (CLI) to manage the database and settings, allowing users to list products, add new products, edit existing products, set the check interval, check specific product prices, and start monitoring prices.

## Features

- **List Products**: Display all tracked products in a table format.
- **Add Product**: Add a new product to the database using its eBay URL.
- **Edit Product**: Update the URL of an existing product in the database.
- **Set Check Interval**: Set the interval for checking prices (default is every 2 hours).
- **Check Price**: Check the current price of a specific product by its ID, with an option to update the price in the database if it has changed.
- **Monitor Prices**: Continuously monitor the prices of all products in the database and send email notifications if any prices change.

## Requirements

- `requests`
- `beautifulsoup4`
- `prettytable`
- `sqlite3` (comes with Python standard library)

Install the required packages using pip:
```bash
pip install requests beautifulsoup4 prettytable
```

## Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/ebay-price-tracker.git
   cd ebay-price-tracker
   ```

2. **List Products**:
   ```bash
   python script_name.py list
   ```

3. **Add Product**:
   ```bash
   python script_name.py add https://www.ebay.com/itm/example_product_id
   ```

4. **Edit Product**:
   ```bash
   python script_name.py edit product_id https://www.ebay.com/itm/new_example_product_id
   ```

5. **Set Check Interval**:
   ```bash
   python script_name.py interval 3600
   ```

6. **Start Monitoring**:
   ```bash
   python script_name.py monitor
   ```

7. **Check Price of a Specific Product**:
   ```bash
   python script_name.py check product_id
   ```

8. **Check and Update Price of a Specific Product**:
   ```bash
   python script_name.py check product_id --update
   ```

## Configuration

- **Email Notification**:
  - Replace `your_email@gmail.com` and `your_email_password` in the `send_email` function with your actual email credentials.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Author

Hamza Alaoui Hamdi
