from flask import Flask, request, render_template, redirect, session, jsonify,url_for,flash
from pymongo import MongoClient
from bson.json_util import dumps
from bson import ObjectId
import datetime
import gridfs
import razorpay
import os

from werkzeug.utils import secure_filename
from email.utils import formataddr


app = Flask(__name__)
app.secret_key = 'secretekeymds#2003'

# Razorpay Configuration
RAZORPAY_KEY_ID = 'rzp_test_5UiHGHfmLCtqOJ'
RAZORPAY_KEY_SECRET = 'TXydG47qdzzNXoyT3gftTXaP'
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Connect to MongoDB
client = MongoClient("mongodb+srv://Akhils2424:Akhils2004@akhil.tjhsyzx.mongodb.net/?retryWrites=true&w=majority&appName=akhil")
db = client['seed_market']
seeds_collection = db['seeds']
user_collection = db["users"]
bookings_collection = db["bookings"]
ratings_collection = db["ratings"]
payments_collection = db["payments"]  # New collection for payment records

@app.route('/company_dashboard')
def company_dashboard():
    seeds = db.seeds.find()
    bookings = bookings_collection.find()
    
    # Get all users
    users = list(db.users.find())

    # Split vendors by verification status
    verified_vendors = [user for user in users if user.get('user_type') == 'vendor' and user.get('verification_status') != 'pending']
    pending_vendors = [user for user in users if user.get('user_type') == 'vendor' and user.get('verification_status') == 'pending']

    # Other user types
    farmers = [user for user in users if user.get('user_type') == 'farmer']
    company = [user for user in users if user.get('user_type') == 'Company']

    return render_template(
        'company_dashboard.html',
        seeds=seeds,
        vendors=verified_vendors,
        pending_vendors=pending_vendors,
        farmers=farmers,
        company=company,
        bookings=bookings
    )
from bson import ObjectId
from flask import request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@app.route('/api/company/vendors/update-status/<vendor_id>', methods=['PUT'])
def update_vendor_status(vendor_id):
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['approved', 'rejected']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    vendor = db.users.find_one({'_id': ObjectId(vendor_id)})
    if not vendor:
        return jsonify({'success': False, 'message': 'Vendor not found'}), 404

    result = db.users.update_one(
        {'_id': ObjectId(vendor_id)},
        {'$set': {'verification_status': new_status}}
    )

    if result.modified_count == 1:
        # Send email after status change
        send_vendor_email(vendor.get('email'), vendor.get('username'), new_status)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Nothing updated'}), 400
    

def send_vendor_email(to_email, vendor_name, status):
    # Replace with your actual email config
    sender_email = 'muralidharas124@gmail.com'
    sender_password = 'axhlpykhgzukyqfm'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    subject = 'Vendor Account Verification Status'
    if status == 'approved':
        message = f"Hello {vendor_name},\n\nYour vendor account has been approved! You can now log in and start using the platform.\n\nThank you!"
    else:
        message = f"Hello {vendor_name},\n\nWe regret to inform you that your vendor account has been rejected.\n\nFor questions, please contact support."

    msg = MIMEMultipart()
    msg['From'] = formataddr(('Farmer Seed selling Platform', sender_email))
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")



# CRUD operations for Seeds
@app.route('/seeds/add', methods=['GET', 'POST'])
def company_add_seed():
    if request.method == 'POST':
        seed_data = {
            'name': request.form['name'],
            'type': request.form['type'],
            'quantity': int(request.form['quantity']),
            'price': float(request.form['price'])
        }
        seeds_collection.insert_one(seed_data)
        return redirect(url_for('company_dashboard'))
    return render_template('add_seed.html')

@app.route('/seeds/edit/<seed_id>', methods=['GET', 'POST'])
def company_edit_seed(seed_id):
    seed = seeds_collection.find_one({'_id': ObjectId(seed_id)})
    if request.method == 'POST':
        updated_data = {
            'name': request.form['name'],
            'type': request.form['type'],
            'quantity': int(request.form['quantity']),
            'price': float(request.form['price'])
        }
        seeds_collection.update_one({'_id': ObjectId(seed_id)}, {'$set': updated_data})
        return redirect(url_for('company_dashboard'))
    return render_template('edit_seed.html', seed=seed)

@app.route('/seeds/delete/<seed_id>', methods=['GET'])
def company_delete_seed(seed_id):
    seeds_collection.delete_one({'_id': ObjectId(seed_id)})
    return redirect(url_for('company_dashboard'))

# CRUD operations for Users
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'role': request.form['role']
        }
        user_collection.insert_one(user_data)
        return redirect(url_for('company_dashboard'))
    return render_template('add_user.html')

@app.route('/users/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = user_collection.find_one({'_id': ObjectId(user_id)})
    if request.method == 'POST':
        updated_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'role': request.form['role']
        }
        user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': updated_data})
        return redirect(url_for('company_dashboard'))
    return render_template('edit_user.html', user=user)

@app.route('/users/delete/<user_id>', methods=['GET'])
def delete_user(user_id):
    user_collection.delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('company_dashboard'))

fs = gridfs.GridFS(db)

@app.route('/')
def index():
    return render_template("auth.html")

@app.route('/login', methods=["POST"])
def login():
    data = request.json
    user = user_collection.find_one({
        "username": data["username"],
        "password": data["password"]
    })
    if user:
        # If user is vendor and verification is pending
        if user["user_type"] == "vendor" and user.get("verification_status") == "pending":
            redirect_url="/pending_verification"
            return jsonify({
                "success": False,
                "message": "",
                "redirect": redirect_url
            })
        
        # Successful login
        session["user_id"] = str(user["_id"])
        session["username"] = user["username"]
        session["user_type"] = user["user_type"]
        
        # Redirect based on user type
        if user["user_type"] == "farmer":
            redirect_url = "/farmer/dashboard"
        elif user["user_type"] == "vendor":
            redirect_url = "/vendor/dashboard"
        else:
            redirect_url = "/company_dashboard"
        
        return jsonify({
            "success": True,
            "message": "Logged in successfully!",
            "redirect": redirect_url
        })

    return jsonify({"success": False, "message": "Invalid username or password."})

@app.route('/pending_verification')
def pending_verification():
    return render_template('pending_verification.html')


@app.route('/farmer/dashboard')
def buyer_dashboard():
    return render_template("farmer_dashboard.html")

@app.route('/signup', methods=["POST"])
def signup():
    data = request.json
    existing_user = user_collection.find_one({"username": data["username"]})
    if existing_user:
        return jsonify({"success": False, "message": "Username already exists."})

    new_user = {
        "username": data["username"],
        "password": data["password"],
        "email":data["email"],
        "mobile": data["mobile"],
        "address": data["address"],
        "user_type": data["user_type"]
    }
    if data["user_type"] == "vendor":
        new_user["verification_status"] = "pending"


    user_collection.insert_one(new_user)
    return jsonify({"success": True, "message": "Signup successful! Please login."})

@app.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/seeds')
def get_seeds():
    seeds = list(seeds_collection.find())
    for seed in seeds:
        seed["_id"] = str(seed["_id"])
        seed["images"] = [f"/image/{img_id}" for img_id in seed.get("images", [])]

        # Add this to fetch vendor (assuming 'user_id' is ObjectId)
        if "user_id" in seed:
            vendor = user_collection.find_one({"_id": seed["user_id"]})
            if vendor:
                seed["user_id"] = {
                    "id": str(vendor["_id"]),
                    "name": vendor.get("name", "Unknown Vendor")
                }
            else:
                seed["user_id"] = {
                    "id": None,
                    "name": "Unknown Vendor"
                }

    return jsonify(seeds)

@app.route('/api/vendorseeds', methods=["GET"])
def get_seeds_farmer():
    user_id = session.get("user_id")
    print(user_id)
    if not user_id:
        return jsonify([])

    # Fetch only seeds created by the current user
    seeds = list(seeds_collection.find({"user_id": user_id}))
    for seed in seeds:
        seed["_id"] = str(seed["_id"])
        seed["images"] = [f"/image/{str(img_id)}" for img_id in seed.get("images", [])]
    return jsonify(seeds)

@app.route('/api/seeds/<string:seed_id>')
def get_seed_by_id(seed_id):
    seed = seeds_collection.find_one({"_id": ObjectId(seed_id)})
    if seed:
        seed["_id"] = str(seed["_id"])
        seed["images"] = [f"/image/{img_id}" for img_id in seed.get("images", [])]
        if "user_id" in seed:
            vendor = user_collection.find_one({"_id": ObjectId(seed["user_id"])})
            if vendor:
                seed["user_id"] = {
                    "id": str(vendor["_id"]),
                    "name": vendor.get("username", "Unknown Vendor")
                }
            else:
                seed["user_id"] = {
                    "id": None,
                    "name": "Name No"
                }
        print(seed)
        return jsonify(seed)
    return jsonify({"error": "Seed not found"}), 404

@app.route("/api/vendor/orders", methods=["GET"])
def get_vendor_orders():
    user_id = session.get("user_id")  # vendor id
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Find all seeds belonging to this vendor
    seeds = list(seeds_collection.find({"user_id": user_id}))
    seed_ids = [seed["_id"] for seed in seeds]

    # Find bookings for these seeds
    bookings = list(bookings_collection.find({"seed_id": {"$in": seed_ids}}))

    enriched_bookings = []

    for b in bookings:
        # Convert IDs to strings
        b["_id"] = str(b["_id"])
        b["seed_id"] = str(b["seed_id"])
        b["user_id"] = str(b["user_id"])
        b["timestamp"] = b["timestamp"].isoformat()

        # Fetch the customer details from users collection
        customer = user_collection.find_one({"_id": ObjectId(b["user_id"])})
        if customer:
            b["customer"] = {
                "name": customer.get("username", "N/A"),
                "phone": customer.get("mobile", "N/A"),
                "address": customer.get("address", "N/A")
            }
        else:
            b["customer"] = {
                "name": "Unknown",
                "phone": "N/A",
                "address": "N/A"
            }

        enriched_bookings.append(b)
        print(enriched_bookings)

    return jsonify(enriched_bookings)

@app.route('/api/users', methods=['POST'])
def company_add_user():
    data = request.get_json()
    username = data.get('username')
    mobile = data.get('mobile')
    usertype = data.get('usertype')
    password = data.get('password')
    address = data.get('address')

    user_data = {
        'username': username,
        'mobile': mobile,
        'user_type': usertype,
        'password': password,
        'address' : address
    }

    result = user_collection.insert_one(user_data)

    return jsonify({'success': True, 'message': 'User added successfully', 'id': str(result.inserted_id)})

@app.route("/api/vendor/orders/<booking_id>", methods=["PUT"])
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Confirmed", "Cancelled" , "Completed"]:
        return jsonify({"error": "Invalid status"}), 400

    result = db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": new_status}}
    )

    if result.matched_count:
        return jsonify({"message": f"Booking {new_status.lower()}"}), 200
    else:
        return jsonify({"error": "Booking not found"}), 404

@app.route('/api/company/vendors/<vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    result = user_collection.delete_one({'_id': ObjectId(vendor_id)})
    return jsonify({'success': result.deleted_count > 0})

@app.route('/api/company/farmers/<farmer_id>', methods=['DELETE'])
def delete_farmer(farmer_id):
    result = user_collection.delete_one({'_id': ObjectId(farmer_id)})
    return jsonify({'success': result.deleted_count > 0})

@app.route('/api/company/users/<user_id>', methods=['DELETE'])
def delete_company_user(user_id):
    result = user_collection.delete_one({'_id': ObjectId(user_id)})
    return jsonify({'success': result.deleted_count > 0})

# New Razorpay Payment Routes
@app.route('/api/create-order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        seed_id = data.get("seed_id")
        booked_quantity = int(data.get("quantity", 0))
        amount = float(data.get("amount", 0))  # Amount in rupees

        # Validate seed existence
        seed = seeds_collection.find_one({"_id": ObjectId(seed_id)})
        if not seed:
            return jsonify({"error": "Seed not found"}), 404

        # Check stock availability
        current_quantity = int(seed.get("quantity", 0))
        if booked_quantity > current_quantity:
            return jsonify({"error": f"Only {current_quantity} units available. Please reduce quantity."}), 400
        elif booked_quantity <= 0:
            return jsonify({"error": "Invalid quantity. Must be greater than 0."}), 400

        # Validate user session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Store order details temporarily (you might want to create a separate orders collection)
        temp_order = {
            "razorpay_order_id": razorpay_order['id'],
            "seed_id": ObjectId(seed_id),
            "seed_name": seed["name"],
            "user_id": user_id,
            "quantity": booked_quantity,
            "amount": amount,
            "status": "created",
            "timestamp": datetime.datetime.utcnow()
        }
        
        # You might want to store this in a separate collection
        db.temp_orders.insert_one(temp_order)

        return jsonify({
            "order_id": razorpay_order['id'],
            "amount": razorpay_order['amount'],
            "currency": razorpay_order['currency'],
            "key": RAZORPAY_KEY_ID
        })

    except Exception as e:
        print("Order creation error:", e)
        return jsonify({"error": "Failed to create order"}), 500

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    try:
        data = request.get_json()
        
        # Get payment details
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
        except:
            return jsonify({"error": "Payment verification failed"}), 400

        # Get the temporary order
        temp_order = db.temp_orders.find_one({"razorpay_order_id": razorpay_order_id})
        if not temp_order:
            return jsonify({"error": "Order not found"}), 404

        # Create the booking
        booking = {
            "seed_id": temp_order["seed_id"],
            "seed_name": temp_order["seed_name"],
            "user_id": temp_order["user_id"],
            "price": temp_order["amount"],
            "quantity": temp_order["quantity"],
            "timestamp": datetime.datetime.utcnow(),
            "status": "Pending",
            "payment_id": razorpay_payment_id,
            "order_id": razorpay_order_id
        }

        bookings_collection.insert_one(booking)

        # Update seed stock
        seeds_collection.update_one(
            {"_id": temp_order["seed_id"]},
            {"$inc": {"quantity": -temp_order["quantity"]}}
        )

        # Store payment record
        payment_record = {
            "payment_id": razorpay_payment_id,
            "order_id": razorpay_order_id,
            "user_id": temp_order["user_id"],
            "amount": temp_order["amount"],
            "status": "completed",
            "timestamp": datetime.datetime.utcnow()
        }
        payments_collection.insert_one(payment_record)

        # Clean up temporary order
        db.temp_orders.delete_one({"razorpay_order_id": razorpay_order_id})

        return jsonify({"message": "Payment successful and booking confirmed"}), 200

    except Exception as e:
        print("Payment verification error:", e)
        return jsonify({"error": "Payment verification failed"}), 500

# Keep existing booking routes for backward compatibility but modify them
@app.route('/api/book', methods=['POST'])
def book_seed():
    # This route is now deprecated in favor of the payment flow
    # But keeping it for any direct booking needs
    return jsonify({"error": "Please use the payment gateway for booking"}), 400

@app.route('/api/bookings')
def get_user_bookings():
    user_id = session.get("user_id")
    print(f"Session user_id: {user_id}")

    if not user_id:
        return jsonify([])

    try:
        # Use ObjectId only if needed; assuming string-based user_id
        bookings = list(bookings_collection.find({"user_id": user_id}))
        print(bookings)
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        return jsonify({"error": "Failed to fetch bookings"}), 500

    enriched_bookings = []

    for booking in bookings:
        booking["_id"] = str(booking["_id"])
        booking["seed_id"] = str(booking["seed_id"])
        booking["user_id"] = str(booking["user_id"])
        booking["timestamp"] = booking.get("timestamp", "")

        # Check if user has already rated this seed
        rating_doc = ratings_collection.find_one({
            "user_id": ObjectId(user_id),
            "seed_id": ObjectId(booking["seed_id"])
        })
        print(rating_doc)

        booking["hasRated"] = bool(rating_doc)
        booking["userRating"] = rating_doc["rating"] if rating_doc else None

        enriched_bookings.append(booking)
    
    print(enriched_bookings)
    return jsonify(enriched_bookings)

@app.route("/api/bookings/<booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    result = bookings_collection.delete_one({"_id": ObjectId(booking_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Booking cancelled"}), 200
    else:
        return jsonify({"error": "Booking not found"}), 404

@app.route("/api/bookings/<booking_id>", methods=["PUT"])
def edit_booking(booking_id):
    data = request.get_json()
    new_quantity = data.get("quantity")

    if not new_quantity or new_quantity < 1:
        return jsonify({"error": "Invalid quantity"}), 400

    booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    price_per_unit = booking["price"] / booking["quantity"]
    new_total_price = round(price_per_unit * new_quantity, 2)

    bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {
            "quantity": new_quantity,
            "price": new_total_price
        }}
    )

    return jsonify({"message": "Booking updated", "new_price": new_total_price}), 200

@app.route("/api/bookings/<booking_id>/rate", methods=["POST"])
def rate_seed(booking_id):
    data = request.get_json()
    rating = int(data.get("rating"))
    user_id = session.get("user_id")

    if not user_id or rating < 1 or rating > 5:
        return jsonify({"error": "Invalid input"}), 400

    booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    if booking.get("status") != "Completed":
        return jsonify({"error": "Only completed bookings can be rated"}), 400

    seed_id = booking["seed_id"]

    # Check if rating already exists for this booking
    existing_rating = ratings_collection.find_one({
        "booking_id": ObjectId(booking_id)
    })

    if existing_rating:
        return jsonify({"error": "This booking has already been rated"}), 400

    # Save new rating with booking_id
    ratings_collection.insert_one({
        "user_id": ObjectId(user_id),
        "seed_id": ObjectId(seed_id),
        "booking_id": ObjectId(booking_id),
        "rating": rating,
        "hasRated": True,
        "timestamp": datetime.datetime.utcnow()
    })

    # Recalculate average rating
    all_ratings = list(ratings_collection.find({"seed_id": ObjectId(seed_id)}))
    rating_values = [r["rating"] for r in all_ratings]
    average = sum(rating_values) / len(rating_values)

    seeds_collection.update_one(
        {"_id": ObjectId(seed_id)},
        {"$set": {
            "rating": round(average, 2),
            "rating_count": len(rating_values)
        }}
    )

    # Flag booking as rated
    bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {
            "hasRated": True,
            "userRating": rating
        }}
    )

    return jsonify({"message": "Rating submitted", "rating": rating})

@app.route("/api/seeds/<seed_id>/rating", methods=["DELETE"])
def delete_rating(seed_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 403

    result = ratings_collection.delete_one({
        "user_id": ObjectId(user_id),
        "seed_id": ObjectId(seed_id)
    })

    if result.deleted_count == 0:
        return jsonify({"error": "Rating not found"}), 404

    # Recalculate average
    all_ratings = list(ratings_collection.find({"seed_id": ObjectId(seed_id)}))
    if all_ratings:
        rating_values = [r["rating"] for r in all_ratings]
        average = sum(rating_values) / len(rating_values)
        count = len(rating_values)
    else:
        average = None
        count = 0

    seeds_collection.update_one(
        {"_id": ObjectId(seed_id)},
        {"$set": {"rating": average, "rating_count": count}}
    )

    return jsonify({"message": "Rating deleted"})

# Add seeds routes
@app.route('/vendor/dashboard')
def farmer_dashboard():
    return render_template('vendor_dashboard.html')

# Assuming the app is already configured with the UPLOAD_FOLDER
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/farmer/add-seed', methods=['POST'])
def add_seed():
    try:
        form = request.form
        name = form['name']
        seed_type = form['seed_type']
        price = float(form['price'])
        quantity = form['quantity']
        video_link = form.get('video_link')
        instructions = form.get('instructions')

        # Handle multiple image uploads
        images = request.files.getlist('images')
        image_ids = []
        for image in images:
            if image:
                filename = secure_filename(image.filename)
                image_id = fs.put(image, filename=filename, content_type=image.content_type)
                image_ids.append(str(image_id))

        seed_data = {
            "name": name,
            "type": seed_type,
            "user_id": session.get("user_id"),
            "price": price,
            "quantity": quantity,
            "video_link": video_link,
            "instructions": instructions,
            "images": image_ids
        }

        seeds_collection.insert_one(seed_data)
        return jsonify({"success": True}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/farmer/delete-seed/<seed_id>', methods=['DELETE'])
def delete_seed(seed_id):
    try:
        # Convert seed_id to ObjectId
        seed_object_id = ObjectId(seed_id)
        
        # Find and delete the seed from the database
        result = seeds_collection.delete_one({"_id": seed_object_id})

        if result.deleted_count > 0:
            return jsonify({"success": True, "message": "Seed deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Seed not found"}), 404

    except Exception as e:
        print(f"Error deleting seed: {e}")
        return jsonify({"success": False, "message": "An error occurred while deleting the seed"}), 500

from flask import Response

@app.route('/image/<image_id>')
def get_image(image_id):
    try:
        image = fs.get(ObjectId(image_id))
        return Response(image.read(), content_type='image/jpeg')
    except Exception as e:
        return "Image not found", 404

if __name__ == '__main__':
    app.run(debug=True)