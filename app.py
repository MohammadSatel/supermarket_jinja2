from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

cart = []

# Load the product_list from the JSON file (or initialize if the file doesn't exist)
try:
    with open('product_list.json', 'r') as product_file:
        product_list = json.load(product_file)
except FileNotFoundError:
    product_list = [
        {"prod_name": "Eggs", "prod_price": 7.95, "quantity": 250},
        {"prod_name": "Milk", "prod_price": 3.75, "quantity": 120},
        {"prod_name": "Cheese", "prod_price": 7.95, "quantity": 175},
        {"prod_name": "Coffee", "prod_price": 5.25, "quantity": 350},
        {"prod_name": "Bread", "prod_price": 2.45, "quantity": 150}
    ]

links = [
    {"prod_name": "Cart", "url": "/cart"},
]

@app.before_request
def save_cart():
    # Serialize and save the cart list to a JSON file
    with open('cart.json', 'w') as cart_file:
        json.dump(cart, cart_file)

@app.teardown_request
def load_cart(exception=None):
    global cart
    try:
        with open('cart.json', 'r') as cart_file:
            cart = json.load(cart_file)
    except FileNotFoundError:
        cart = []

@app.route('/')
def homepage():
    return render_template('index.html', links=links, product_list=product_list)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    if request.method == 'POST':
        selected_product_name = request.form.get('product_name')
        selected_product = next((product for product in product_list if product['prod_name'] == selected_product_name), None)
        if selected_product and selected_product['quantity'] > 0:
            cart_item = next((item for item in cart if item['prod_name'] == selected_product_name), None)
            if cart_item:
                if cart_item['cart_quantity'] < selected_product['quantity']:
                    cart_item['cart_quantity'] += 1
            else:
                cart.append({
                    'prod_name': selected_product_name,
                    'prod_price': selected_product['prod_price'],
                    'cart_quantity': 1
                })

    # Calculate the total item count
    total_items = sum(item.get('cart_quantity', 0) for item in cart)

    # Calculate the accurate total cost of items in the cart
    total_cost = sum(item['prod_price'] * item['cart_quantity'] for item in cart)

    return render_template('cart.html', links=links, cart=cart, total_items=total_items, total_cost=total_cost)

@app.route('/buy', methods=['POST'])
def buy():
    global cart, product_list

    # Update the quantity of products in the product list and remove products from the cart
    for item in cart:
        selected_product = next((product for product in product_list if product['prod_name'] == item['prod_name']), None)
        if selected_product:
            selected_product['quantity'] -= item.get('cart_quantity', 0)

    cart = []  # Empty the cart list

    # Save the updated product_list to a JSON file
    with open('product_list.json', 'w') as product_file:
        json.dump(product_list, product_file)

    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    app.run(debug=True)
