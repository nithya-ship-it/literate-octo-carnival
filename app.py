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

        GLOMOPAY_API_KEY = os.environ.get('GLOMOPAY_API_KEY')
        
        if not GLOMOPAY_API_KEY:
            logger.error("GLOMOPAY_API_KEY not set in environment variables")
            return jsonify({
                "error": "Payment system not configured"
            }), 500

        # STEP 1: Create customer in GlomoPay
        customer_payload = {
            "email": customer_email,
            "name": customer_email.split('@')[0].title()  # Use email prefix as name
        }

        logger.info(f"Creating GlomoPay customer: {customer_email}")

        customer_response = requests.post(
            'https://api.glomopay.com/api/v1/customers',
            headers={
                'Authorization': f'Bearer {GLOMOPAY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json=customer_payload,
            timeout=15
        )

        logger.info(f"GlomoPay customer response status: {customer_response.status_code}")

        if customer_response.status_code not in [200, 201]:
            logger.error(f"Failed to create customer: {customer_response.text}")
            return jsonify({
                "error": "Failed to create customer account",
                "details": customer_response.text
            }), 500

        customer_data = customer_response.json()
        customer_id = customer_data.get('id')

        if not customer_id:
            logger.error(f"No customer ID in response: {customer_data}")
            return jsonify({
                "error": "Failed to get customer ID"
            }), 500

        # STEP 2: Create payment link with real customer_id
        expires_at = (datetime.utcnow() + timedelta(days=180)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

        glomopay_payload = {
            "customer_id": customer_id,  # Real customer ID from GlomoPay
            "payment_methods": ["card"],
            "currency": "USD",
            "amount": int(product['price'] * 100),
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

        response = requests.post(
            'https://api.glomopay.com/api/v1/payin',
            headers={
                'Authorization': f'Bearer {GLOMOPAY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json=glomopay_payload,
            timeout=15
        )

        logger.info(f"GlomoPay payment link response status: {response.status_code}")

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
                "status_code": response.status_code,
                "details": response.text
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
