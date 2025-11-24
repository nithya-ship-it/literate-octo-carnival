from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PRODUCTS = [
    {
        "id": "prod_001",
        "name": "AirPods Pro",
        "brand": "Apple",
        "price": 249.99,
        "description": "wireless earbuds with active noise cancellation, wireless charging case, spatial audio",
        "category": "earbuds",
        "image": "🎧"
    },
    {
        "id": "prod_002",
        "name": "Galaxy Buds Pro",
        "brand": "Samsung",
        "price": 199.99,
        "description": "wireless earbuds with intelligent ANC, 360 audio, IPX7 water resistance",
        "category": "earbuds",
        "image": "🎧"
    },
    {
        "id": "prod_003",
        "name": "MacBook Air M2",
        "brand": "Apple",
        "price": 1199.99,
        "description": "M2 chip, 13.6-inch Liquid Retina display, 8GB RAM, 256GB SSD",
        "category": "laptops",
        "image": "💻"
    },
    {
        "id": "prod_004",
        "name": "Sony WH-1000XM5",
        "brand": "Sony",
        "price": 399.99,
        "description": "industry-leading noise cancellation, 30-hour battery life, premium sound",
        "category": "headphones",
        "image": "🎧"
    },
    {
        "id": "prod_005",
        "name": "Dell XPS 15",
        "brand": "Dell",
        "price": 1499.99,
        "description": "15.6-inch 4K display, Intel i7, 16GB RAM, 512GB SSD",
        "category": "laptops",
        "image": "💻"
    },
    {
        "id": "prod_006",
        "name": "Bose QuietComfort Earbuds II",
        "brand": "Bose",
        "price": 299.99,
        "description": "wireless earbuds with personalized noise cancellation, comfortable fit, excellent audio quality",
        "category": "earbuds",
        "image": "🎧"
    }
]

@app.route('/')
def home():
    return jsonify({
        "status": "✅ API is running",
        "message": "GlomoPay Shopping Assistant API",
        "version": "2.0.0",
        "endpoints": {
            "search": "POST /api/products/search",
            "checkout": "POST /api/checkout/create",
            "all_products": "GET /api/products"
        }
    })

@app.route('/api/products/search', methods=['POST'])
def search_products():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' parameter in request body"
            }), 400
        
        query = data['query'].lower().strip()
        
        if not query:
            return jsonify({
                "error": "Query cannot be empty"
            }), 400
        
        # Split query into words and remove price/filter words
        stop_words = {'under', 'over', 'below', 'above', 'around', 'the', 'a', 'an'}
        query_words = [word for word in query.split() if word not in stop_words and not word.startswith('$') and not word.replace('.', '').isdigit()]
        
        # If no valid words remain, use original query
        if not query_words:
            query_words = [query]
        
        matching_products = []
        for product in PRODUCTS:
            product_text = f"{product['name']} {product['brand']} {product['category']} {product['description']}".lower()
            
            # Match if ANY query word is found in product text
            if any(word in product_text for word in query_words):
                matching_products.append(product)
        
        return jsonify({
            "success": True,
            "query": query,
            "count": len(matching_products),
            "products": matching_products
        }), 200
        
    except Exception as e:
        logger.error(f"Error in product search: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An error occurred while searching for products"
        }), 500

@app.route('/api/checkout/create', methods=['POST'])
def create_checkout():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        product_id = data.get('product_id')
        customer_email = data.get('customer_email')
        customer_phone = data.get('customer_phone')

        if not product_id:
            return jsonify({"error": "Missing 'product_id' parameter"}), 400

        if not customer_email:
            return jsonify({"error": "Missing 'customer_email' parameter"}), 400

        if not customer_phone:
            return jsonify({"error": "Missing 'customer_phone' parameter"}), 400

        # Format phone number with +91 prefix for India
        customer_phone_clean = customer_phone.replace('-', '').replace(' ', '').replace('+', '')
        if not customer_phone_clean.startswith('91'):
            customer_phone_formatted = f"+91-{customer_phone_clean}"
        else:
            customer_phone_formatted = f"+{customer_phone_clean[:2]}-{customer_phone_clean[2:]}"

        product = next((p for p in PRODUCTS if p['id'] == product_id), None)

        if not product:
            return jsonify({"error": f"Product with id '{product_id}' not found"}), 404

        GLOMOPAY_API_KEY = os.environ.get('GLOMOPAY_API_KEY')
        
        if not GLOMOPAY_API_KEY:
            logger.error("GLOMOPAY_API_KEY not set")
            return jsonify({"error": "Payment system not configured"}), 500

        try:
            # STEP 1: Create customer with real phone number
            customer_name = customer_email.split('@')[0].title()
            customer_payload = {
                "name": customer_name,
                "customer_type": "individual",
                "email": customer_email,
                "phone": customer_phone_formatted,
                "address": "123 Main Street",
                "city": "Bangalore",
                "state": "Karnataka",
                "country": "IND",
                "pincode": "560001"
            }

            logger.info(f"Creating customer: {customer_email} with phone: {customer_phone_formatted}")

            customer_response = requests.post(
                'https://staging-api.glomopay.com/api/v1/customer',
                headers={
                    'Authorization': f'Bearer {GLOMOPAY_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json=customer_payload,
                timeout=15
            )

            logger.info(f"Customer creation status: {customer_response.status_code}")
            logger.info(f"Customer creation response: {customer_response.text}")

            if customer_response.status_code not in [200, 201]:
                logger.error(f"Customer creation failed: {customer_response.text}")
                return jsonify({
                    "error": "Failed to create customer",
                    "details": customer_response.text
                }), 500

            customer_data = customer_response.json()
            customer_id = customer_data.get('id')

            if not customer_id:
                logger.error(f"No customer ID in response: {customer_data}")
                return jsonify({"error": "Failed to get customer ID"}), 500

            logger.info(f"Customer created successfully: {customer_id}")

        except Exception as e:
            logger.error(f"Customer creation error: {str(e)}")
            return jsonify({"error": f"Customer creation failed: {str(e)}"}), 500

        # STEP 2: Create payment link with real customer_id
        try:
            expires_at = (datetime.utcnow() + timedelta(days=180)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

            payment_payload = {
                "customer_id": customer_id,
                "payment_methods": ["card"],
                "currency": "USD",
                "amount": int(product['price'] * 100),
                "purpose_code": "P1401",
                "invoice_description": f"{product['brand']} {product['name']}",
                "reference_number": f"REF_{product_id}_{int(datetime.utcnow().timestamp())}",
                "expires_at": expires_at,
                "product": {
                    "name": f"{product['brand']} {product['name']}",
                    "description": product['description']
                },
                "notes": {
                    "product_id": product_id,
                    "customer_email": customer_email,
                    "customer_phone": customer_phone_formatted
                }
            }

            logger.info(f"Creating payment link for product: {product_id}")

            payment_response = requests.post(
                'https://staging-api.glomopay.com/api/v1/payin',
                headers={
                    'Authorization': f'Bearer {GLOMOPAY_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json=payment_payload,
                timeout=15
            )

            logger.info(f"Payment link creation status: {payment_response.status_code}")
            logger.info(f"Payment link response: {payment_response.text}")

            if payment_response.status_code in [200, 201]:
                payment_data = payment_response.json()
                payment_link = payment_data.get('payment_link')
                
                if not payment_link:
                    logger.warning(f"No payment_link in response: {payment_data}")
                    return jsonify({
                        "error": "Payment link not generated yet",
                        "status": payment_data.get('status'),
                        "details": "Payment may require manual review"
                    }), 500

                return jsonify({
                    "success": True,
                    "checkout_id": payment_data.get('id'),
                    "product_id": product_id,
                    "product_name": product['name'],
                    "brand": product['brand'],
                    "price": product['price'],
                    "customer_email": customer_email,
                    "checkout_url": payment_link,
                    "status": payment_data.get('status'),
                    "expires_at": payment_data.get('expires_at'),
                    "message": f"Ready to purchase {product['brand']} {product['name']} for ${product['price']}"
                }), 200
            else:
                logger.error(f"Payment link creation failed: {payment_response.text}")
                return jsonify({
                    "error": "Failed to create payment link",
                    "status_code": payment_response.status_code,
                    "details": payment_response.text
                }), 500

        except Exception as e:
            logger.error(f"Payment link error: {str(e)}")
            return jsonify({"error": f"Payment link creation failed: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Checkout error: {str(e)}", exc_info=True)
        return jsonify({"error": "Checkout failed"}), 500

@app.route('/api/products', methods=['GET'])
def get_all_products():
    return jsonify({
        "success": True,
        "count": len(PRODUCTS),
        "products": PRODUCTS
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
