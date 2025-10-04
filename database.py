"""
Stores user packages.
"""
import random 

class Item:
    def __init__(self, id, user_email, seller, product_name, status):
        self.id = id
        self.user_email = user_email
        self.seller = seller
        self.product_name = product_name
        self.status = status


# Generate 26 user emails
letters = "abcdefghijklmnopqrstuvwxyz"
user_emails = [f"{l}@gmail.com" for l in letters]

# some sellers
sellers = [
    "nike", 
    "uniqlo", 
    "gucci", 
    "adidas", 
    "gap", 
    "old navy",
    "prada",
    "american eagle"
]

# 20 products  
products = [
    "tshirt",
    "tank top",
    "blouse",
    "shirt",
    "sweater",
    "hoodie",
    "cardigan",
    "jeans",
    "pants",
    "leggings",
    "trousers",
    "shorts",
    "skirt",
    "jacket",
    "coat",
    "blazer",
    "dress",
    "jumpsuit",
    "underwear",
    "pajamas",
    "socks",
    "headband",
    "mittens"
]


status = [
    "order placed",
    "packaged",
    "shippped",
    "out for delivery",
    "delivered"
]


# Generate a database of orders to work with
all_orders = {}
user_orders = {}

id_num = 0

for email in user_emails:
    user_orders[email] = []
    for seller in sellers:
        for product in products:
            progress = random.choice(status)
            order = Item(id_num, email, seller, product, progress)
            all_orders[id_num] = order
            user_orders[email].append(order)
            id_num += 1
    


