# InterBase Driver for Python

<a href="https://www.embarcadero.com/br/products/interbase"><img alt="InterBase" src="https://d2ohlsp9gwqc7h.cloudfront.net/images/logos/logo-page/ib-logo-1024.png" align="right" width="250"></a>

> A powerful, [PEP-249-compliant](https://peps.python.org/pep-0249/) Python driver for **InterBase**, supporting both 32-bit and 64-bit.

The **InterBase Driver for Python** is based on the [FDB driver](http://www.firebirdsql.org/en/devel-python-driver/) and provides access to the [InterBase](https://interbase.com/) RDBMS using a robust and flexible Python interface. This package supports the **Python Database API 2.0** standard (PEP-249) while offering extended access to the native InterBase API.

📚 [InterBase Documentation](https://docwiki.embarcadero.com/InterBase/2020/en/Main_Page)  
🔗 [GitHub Source Code](https://github.com/Embarcadero/InterBasePython)

---

## ✨ Features

- PEP-249 compliance  
- Full Unicode and character set support  
- Native API access  
- Multiple independent transactions per connection  
- Distributed transaction support  
- Automatic conversion of textual data  
- Prepared statement support

---

## 📦 Installation

> Requires Python 3.x (32-bit or 64-bit version to match InterBase client).

Install via PyPI:
```bash
pip install interbase
```

Or install from the GitHub repository:
```bash
pip install git+https://github.com/Embarcadero/InterBasePython.git
# or via SSH:
pip install git+ssh://git@github.com/Embarcadero/InterBasePython.git
```

---

## 🧪 Setting Up a Test Database

```bash
cd test/files
isql -i create-test-db.sql
```

---

## 🔌 Sample Usage

### Basic Connection
```python
import interbase

con = interbase.connect(
    host=IBTEST_HOST,                   # Hostname or IP address of the InterBase server
    database=IBTEST_DB_PATH,            # Path to the database file on the server
    user=IBTEST_USER,                   # Username for authentication
    password=IBTEST_PASSWORD,           # Password for authentication
    sql_dialect=IBTEST_SQL_DIALECT,     # SQL dialect to use (usually 1 or 3)
    ssl=IBTEST_SERVER_PUBLIC_FILE is not None,         # Enable SSL if a public server key is provided
    server_public_file=IBTEST_SERVER_PUBLIC_FILE       # Path to the server's public SSL key file (if SSL is enabled)
)
```

### Executing a Query
```python
cur = con.cursor()
cur.execute("SELECT * FROM employees")
for row in cur:
    print(row)
```

### Using Parameters
```python
cur.execute("INSERT INTO employees(name, age) VALUES (?, ?)", ("John Doe", 34))
con.commit()
```

### Handling Transactions

#### Manual Transaction Control
```python
transaction = con.main_transaction
transaction.begin()

cursor = transaction.cursor()
cursor.execute("INSERT INTO t (c1) VALUES (1)")
transaction.commit()
```

#### Using a Context Manager
```python
import interbase

with interbase.TransactionContext(con) as tr:
    cursor = tr.cursor()
    cursor.execute("INSERT INTO t (c1) VALUES (1)")
# The transaction is automatically committed when the block ends.
```

---

## 🧰 More Examples
Explore the `test` folder in the [GitHub Repository](https://github.com/Embarcadero/InterBasePython) for full coverage of features, including:

- Working with BLOBs  
- Using metadata APIs  
- Working with stored procedures  
- SSL support  
- Error handling  

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License
This project is licensed under the Embarcadero license terms.

---

> 🔗 Stay up to date with the latest changes and enhancements to InterBase by following the official [Embarcadero Blog](https://blogs.embarcadero.com/).
