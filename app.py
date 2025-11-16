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
        "description": "Wireless earbuds with active noise cancellation, wireless charging case, spatial audio",
        "category": "earbuds",
        "image": "🎧"
    },
    {
        "id": "prod_002",
        "name": "Galaxy Buds Pro",
        "brand": "Samsung",
        "price": 199.99,
        "description": "Wireless earbuds with intelligent ANC, 360 audio, IPX7 water resistance",
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
        "description": "Industry-leading noise cancellation, 30-hour battery life, premium sound",
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
        "description": "Wireless earbuds with personalized noise cancellation, comfortable fit, excellent audio quality",
        "category": "earbuds",
        "image": "🎧"
    }
]

@app.route('/')
def home():
    return jsonify({
        "status": "✅ API is running",
        "message": "GlomoPay Shopping Assistant API",
        "version": "1.0.0",
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
        
        matching_products = [
            product for product in PRODUCTS
            if query in product['name'].lower() or
               query in product['brand'].lower() or
               query in product['category'].lower() or
               query in product['description'].lower()
        ]
        
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
            return jsonify({
                "error": "Request body is required"
            }), 400

        product_id = data.get('product_id')
        customer_email = data.get('customer_email')

        if not product_id:
            return jsonify({
                "error": "Missing 'product_id' parameter"
            }), 400

        if not customer_email:
            return jsonify({
                "error": "Missing 'customer_email' parameter"
            }), 400

        product = next((p for p in PRODUCTS if p['id'] == product_id), None)

        if not product:
            return jsonify({
                "error": f"Product with id '{product_id}' not found"
            }), 404

        # Get GlomoPay API key from environment variable
        GLOMOPAY_API_KEY = os.environ.get('GLOMOPAY_API_KEY')
        
        if not GLOMOPAY_API_KEY:
            logger.error("GLOMOPAY_API_KEY not set in environment variables")
            return jsonify({
                "error": "Payment system not configured"
            }), 500

        # Calculate expiry date (6 months from now)
        expires_at = (datetime.utcnow() + timedelta(days=180)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

        # Prepare GlomoPay Payment Link request
        glomopay_payload = {
            "customer_id": f"cust_{hash(customer_email) % 1000000}",
            "payment_methods": ["card"],
            "currency": "USD",
            "amount": int(product['price'] * 100),  # Convert to cents
            "purpose_code": "P1401",
            "invoice_description": f"{product['brand']} {product['name']} - {product['description']}",
            "reference_number": f"REF_{product_id}_{int(datetime.utcnow().timestamp())}",
            "expires_at": expires_at,
            "product": {
                "name": f"{product['brand']} {product['name']}",
                "description": product['description']
            },
            "notes": {
                "product_id": product_id,
                "customer_email": customer_email,
                "product_name": product['name']
            }
        }

        logger.info(f"Creating GlomoPay Payment Link for product: {product_id}")

        # Call GlomoPay Payment Link API
        response = requests.post(
            'https://api.glomopay.com/api/v1/payin',
            headers={
                'Authorization': f'Bearer {GLOMOPAY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json=glomopay_payload,
            timeout=15
        )

        logger.info(f"GlomoPay response status: {response.status_code}")

        if response.status_code in [200, 201]:
            glomopay_data = response.json()
            
            payment_link = glomopay_data.get('payment_link')
            
            if not payment_link:
                logger.warning(f"No payment_link in response. Status: {glomopay_data.get('status')}")
                return jsonify({
                    "error": "Payment link not generated yet",
                    "status": glomopay_data.get('status'),
                    "details": "Payment may require manual review by GlomoPay"
                }), 500

            checkout_session = {
                "success": True,
                "checkout_id": glomopay_data.get('id'),
                "product_id": product_id,
                "product_name": product['name'],
                "brand": product['brand'],
                "price": product['price'],
                "customer_email": customer_email,
                "checkout_url": payment_link,
                "status": glomopay_data.get('status'),
                "expires_at": glomopay_data.get('expires_at'),
                "message": f"Ready to purchase {product['brand']} {product['name']} for ${product['price']}"
            }

            logger.info(f"Successfully created payment link")
            return jsonify(checkout_session), 200
            
        else:
            logger.error(f"GlomoPay API error: {response.status_code} - {response.text}")
            return jsonify({
                "error": "Failed to create payment link",
                "status_code": response.status_code
            }), 500

    except requests.RequestException as e:
        logger.error(f"Error calling GlomoPay API: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to connect to GlomoPay"
        }), 500
    except Exception as e:
        logger.error(f"Error in checkout creation: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An error occurred while creating checkout session"
        }), 500

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
