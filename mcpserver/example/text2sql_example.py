import random
import sqlite3

from faker import Faker

# 初始化 Faker 实例
fake = Faker('zh_CN')
import pandas as pd

exampleDDl = """
-- 用户主表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT -- 描述用户备注信息
);

-- 用户详细资料（一对一）
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    gender TEXT,
    birth_date DATE,
    bio TEXT,
    remark TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 用户地址（一对多）
CREATE TABLE IF NOT EXISTS user_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    remark TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 用户订单（一对多）
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_number TEXT NOT NULL UNIQUE,
    total_amount REAL DEFAULT 0.0,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 商品信息表
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT
);

-- 订单明细（订单与商品之间的多对多关系）
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    subtotal REAL NOT NULL,
    remark TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

-- 用户名和邮箱的唯一索引已存在（UNIQUE约束自动创建了索引）

-- 用户地址：按用户ID和城市查询
CREATE INDEX IF NOT EXISTS idx_user_addresses_user_id ON user_addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_user_addresses_city ON user_addresses(city);

-- 订单：按用户ID和状态查询
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- 商品：按名称和价格范围查询
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);

-- 订单明细：按订单和商品ID查询
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

"""
conn = sqlite3.connect('./example.db')

# 创建一个 cursor 对象，用于执行 SQL 命令
cursor = conn.cursor()

cursor.executescript(exampleDDl)


def table_has_data(table_name):
    """检查表是否有数据"""
    cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
    return cursor.fetchone() is not None


def generate_users(n=10):
    if table_has_data("users"):
        print("ℹ️ users 表已有数据，跳过插入")
        return

    users = []
    for _ in range(n):
        username = fake.user_name()
        email = fake.email()
        created_at = fake.date_between(start_date='-1y', end_date='today')
        remark = fake.sentence(nb_words=6)
        users.append((username, email, created_at, remark))
    cursor.executemany('''
        INSERT INTO users (username, email, created_at, remark)
        VALUES (?, ?, ?, ?)
    ''', users)
    conn.commit()
    print(f"✅ {n} 条用户数据已插入")


def generate_user_profiles():
    if table_has_data("user_profiles"):
        print("ℹ️ user_profiles 表已有数据，跳过插入")
        return

    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    profiles = []
    for user_id in user_ids:
        full_name = fake.name()
        gender = random.choice(['男', '女'])
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=70)
        bio = fake.text(max_nb_chars=200)
        remark = fake.sentence(nb_words=5)
        profiles.append((user_id, full_name, gender, birth_date, bio, remark))

    cursor.executemany('''
        INSERT INTO user_profiles (user_id, full_name, gender, birth_date, bio, remark)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', profiles)
    conn.commit()
    print(f"✅ 用户资料数据已插入")


def generate_user_addresses():
    if table_has_data("user_addresses"):
        print("ℹ️ user_addresses 表已有数据，跳过插入")
        return

    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    addresses = []
    for user_id in user_ids:
        for _ in range(random.randint(1, 3)):  # 每个用户1-3个地址
            address_line1 = fake.street_address()
            address_line2 = f"单元 {fake.random_int(min=1, max=5)} 号" if random.random() > 0.7 else None
            city = fake.city()
            postal_code = fake.postcode()
            is_default = random.choice([0, 1])
            remark = fake.sentence(nb_words=4)
            addresses.append((user_id, address_line1, address_line2, city, postal_code, is_default, remark))

    cursor.executemany('''
        INSERT INTO user_addresses 
        (user_id, address_line1, address_line2, city, postal_code, is_default, remark)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', addresses)
    conn.commit()
    print(f"✅ 用户地址数据已插入")


def generate_products(n=20):
    if table_has_data("products"):
        print("ℹ️ products 表已有数据，跳过插入")
        return

    products = []
    for _ in range(n):
        name = fake.word().capitalize() + " " + fake.random_element(elements=('手机', '耳机', '手表', '电脑', '平板'))
        description = fake.text(max_nb_chars=100)
        price = round(random.uniform(10, 1000), 2)
        stock = random.randint(0, 100)
        created_at = fake.date_between(start_date='-2y', end_date='today')
        remark = fake.sentence(nb_words=5)
        products.append((name, description, price, stock, created_at, remark))

    cursor.executemany('''
        INSERT INTO products (name, description, price, stock, created_at, remark)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', products)
    conn.commit()
    print(f"✅ {n} 条商品数据已插入")


def generate_orders(n=30):
    if table_has_data("orders"):
        print("ℹ️ orders 表已有数据，跳过插入")
        return

    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    orders = []
    order_numbers = set()

    for _ in range(n):
        while True:
            order_number = f"ORD-{fake.random_int(min=10000, max=99999)}"
            if order_number not in order_numbers:
                order_numbers.add(order_number)
                break
        user_id = random.choice(user_ids)
        total_amount = round(random.uniform(50, 2000), 2)
        status = random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled'])
        created_at = fake.date_between(start_date='-6m', end_date='today')
        remark = fake.sentence(nb_words=5)
        orders.append((order_number, user_id, total_amount, status, created_at, remark))

    cursor.executemany('''
        INSERT INTO orders (order_number, user_id, total_amount, status, created_at, remark)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', orders)
    conn.commit()
    print(f"✅ {n} 条订单数据已插入")


def generate_order_items():
    if table_has_data("order_items"):
        print("ℹ️ order_items 表已有数据，跳过插入")
        return

    cursor.execute("SELECT id FROM orders")
    order_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM products")
    product_ids = [row[0] for row in cursor.fetchall()]

    order_items = []
    for order_id in order_ids:
        num_items = random.randint(1, 5)  # 每个订单1-5个商品
        selected_products = random.sample(product_ids, k=num_items)

        for product_id in selected_products:
            quantity = random.randint(1, 3)
            cursor.execute("SELECT price FROM products WHERE id=?", (product_id,))
            price = cursor.fetchone()[0]
            subtotal = round(price * quantity, 2)
            remark = fake.sentence(nb_words=4)
            order_items.append((order_id, product_id, quantity, subtotal, remark))

    cursor.executemany('''
        INSERT INTO order_items (order_id, product_id, quantity, subtotal, remark)
        VALUES (?, ?, ?, ?, ?)
    ''', order_items)
    conn.commit()
    print(f"✅ 订单明细数据已插入")


generate_users(10)
generate_user_profiles()
generate_user_addresses()
generate_products(20)
generate_orders(30)
generate_order_items()


def get_data_base_ddl():
    """返回数据库的结构"""
    return exampleDDl


def execute_select_sql(sql: str) -> str:
    """
    接受一个 SELECT SQL 字符串，执行查询，并返回 Markdown 格式的表格字符串。
    仅支持 SELECT 查询语句。
    """

    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")

    try:
        df = pd.read_sql_query(sql, conn)
        if df.empty:
            return "查询结果为空。"
        return df.to_markdown(index=False)
    except Exception as e:
        return f"执行错误：{str(e)}"
