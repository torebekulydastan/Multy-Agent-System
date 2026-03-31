DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS product_catalog;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    city VARCHAR(50),
    age INT CHECK (age > 0),
    registration_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL
);

CREATE TABLE product_catalog (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(120) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    brand VARCHAR(50),
    created_at DATE NOT NULL
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    total_amount NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),
    transaction_date DATE NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    transaction_status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_product
        FOREIGN KEY (product_id) REFERENCES product_catalog(product_id)
        ON DELETE CASCADE
);

INSERT INTO users (full_name, email, city, age, registration_date, status) VALUES
('Aruzhan Sarsen', 'aruzhan.sarsen@example.com', 'Almaty', 21, '2025-01-15', 'active'),
('Dias Nurpeis', 'dias.nurpeis@example.com', 'Astana', 24, '2025-02-10', 'active'),
('Madina Tolegen', 'madina.tolegen@example.com', 'Shymkent', 22, '2025-03-05', 'active'),
('Nursultan Bekov', 'nursultan.bekov@example.com', 'Karaganda', 27, '2025-01-28', 'inactive'),
('Aigerim Zhaksy', 'aigerim.zhaksy@example.com', 'Almaty', 20, '2025-04-02', 'active'),
('Ruslan Kuat', 'ruslan.kuat@example.com', 'Aktobe', 29, '2025-02-18', 'active'),
('Dana Yermek', 'dana.yermek@example.com', 'Taraz', 23, '2025-03-22', 'blocked'),
('Askar Sapar', 'askar.sapar@example.com', 'Atyrau', 31, '2025-01-30', 'active'),
('Tomiris Kassen', 'tomiris.kassen@example.com', 'Kokshetau', 19, '2025-04-10', 'active'),
('Alibek Serik', 'alibek.serik@example.com', 'Pavlodar', 26, '2025-02-26', 'inactive'),
('Saltanat Zhunis', 'saltanat.zhunis@example.com', 'Almaty', 25, '2025-05-01', 'active'),
('Miras Ospan', 'miras.ospan@example.com', 'Astana', 28, '2025-03-11', 'active'),
('Zarina Auel', 'zarina.auel@example.com', 'Semey', 22, '2025-01-09', 'active'),
('Adil Tursyn', 'adil.tursyn@example.com', 'Turkistan', 30, '2025-02-14', 'blocked'),
('Amina Dastan', 'amina.dastan@example.com', 'Almaty', 18, '2025-04-25', 'active'),
('Yeldos Aman', 'yeldos.aman@example.com', 'Kostanay', 27, '2025-03-17', 'active'),
('Kamila Nurgali', 'kamila.nurgali@example.com', 'Petropavl', 24, '2025-02-07', 'inactive'),
('Sanzhar Utep', 'sanzhar.utep@example.com', 'Oral', 32, '2025-01-19', 'active'),
('Ayaulym Tlegen', 'ayaulym.tlegen@example.com', 'Almaty', 21, '2025-05-08', 'active'),
('Ermek Baizak', 'ermek.baizak@example.com', 'Astana', 29, '2025-03-29', 'active');

INSERT INTO product_catalog (product_name, category, price, stock_quantity, brand, created_at) VALUES
('iPhone 15', 'Electronics', 499999.00, 15, 'Apple', '2025-01-01'),
('Galaxy S24', 'Electronics', 429990.00, 20, 'Samsung', '2025-01-03'),
('AirPods Pro', 'Accessories', 129990.00, 30, 'Apple', '2025-01-05'),
('Gaming Mouse G102', 'Accessories', 15990.00, 50, 'Logitech', '2025-01-07'),
('Mechanical Keyboard K8', 'Accessories', 45990.00, 25, 'Keychron', '2025-01-10'),
('ThinkPad X1', 'Laptops', 899990.00, 10, 'Lenovo', '2025-01-11'),
('MacBook Air M3', 'Laptops', 749990.00, 12, 'Apple', '2025-01-12'),
('Dell XPS 13', 'Laptops', 799990.00, 8, 'Dell', '2025-01-13'),
('Office Chair Comfort', 'Furniture', 89990.00, 18, 'ErgoHome', '2025-01-14'),
('Standing Desk Pro', 'Furniture', 189990.00, 7, 'WorkSpace', '2025-01-15'),
('Notebook A5', 'Stationery', 1490.00, 200, 'OfficeBox', '2025-01-16'),
('Gel Pen Set', 'Stationery', 2490.00, 180, 'Pilot', '2025-01-17'),
('Monitor 27 inch', 'Electronics', 124990.00, 16, 'LG', '2025-01-18'),
('USB-C Hub', 'Accessories', 12990.00, 45, 'Ugreen', '2025-01-19'),
('External SSD 1TB', 'Storage', 54990.00, 22, 'Samsung', '2025-01-20'),
('Water Bottle', 'Lifestyle', 4990.00, 90, 'HydroMax', '2025-01-21'),
('Backpack Urban', 'Lifestyle', 24990.00, 40, 'MarkRyden', '2025-01-22'),
('Webcam HD', 'Electronics', 32990.00, 28, 'Logitech', '2025-01-23'),
('Tablet S9', 'Electronics', 319990.00, 14, 'Samsung', '2025-01-24'),
('Printer LaserJet', 'Office Equipment', 139990.00, 9, 'HP', '2025-01-25');

INSERT INTO transactions (user_id, product_id, quantity, total_amount, transaction_date, payment_method, transaction_status) VALUES
(1, 1, 1, 499999.00, '2025-05-10', 'card', 'completed'),
(2, 3, 1, 129990.00, '2025-05-11', 'cash', 'completed'),
(3, 4, 2, 31980.00, '2025-05-12', 'card', 'completed'),
(4, 10, 1, 189990.00, '2025-05-13', 'bank_transfer', 'pending'),
(5, 11, 5, 7450.00, '2025-05-14', 'card', 'completed'),
(6, 7, 1, 749990.00, '2025-05-15', 'card', 'completed'),
(7, 15, 2, 109980.00, '2025-05-16', 'cash', 'cancelled'),
(8, 9, 1, 89990.00, '2025-05-17', 'card', 'completed'),
(9, 16, 3, 14970.00, '2025-05-18', 'mobile_payment', 'completed'),
(10, 2, 1, 429990.00, '2025-05-19', 'card', 'completed'),
(11, 18, 1, 32990.00, '2025-05-20', 'bank_transfer', 'pending'),
(12, 13, 2, 249980.00, '2025-05-21', 'card', 'completed'),
(13, 6, 1, 899990.00, '2025-05-22', 'card', 'completed'),
(14, 14, 2, 25980.00, '2025-05-23', 'cash', 'completed'),
(15, 17, 1, 24990.00, '2025-05-24', 'mobile_payment', 'completed'),
(16, 20, 1, 139990.00, '2025-05-25', 'card', 'completed'),
(17, 5, 1, 45990.00, '2025-05-26', 'bank_transfer', 'cancelled'),
(18, 8, 1, 799990.00, '2025-05-27', 'card', 'completed'),
(19, 12, 4, 9960.00, '2025-05-28', 'cash', 'completed'),
(20, 19, 1, 319990.00, '2025-05-29', 'card', 'pending');