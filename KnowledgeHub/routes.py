import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, jsonify, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from models import Course, User, Purchase
import stripe
import secrets
from authlib.integrations.base_client.errors import OAuthError

load_dotenv()

random_password = secrets.token_hex(16)
stripe.api_key = os.getenv("STRIPE_API_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app, db, bcrypt, oauth):
    @app.route('/')
    @login_required
    def index():
        courses = Course.query.all()
        return render_template('index.html', courses=courses)
    
    ## USING GOOGLE--------------------------
    @app.route('/google_login')
    def google_login():
        try:
            if current_user.is_authenticated:
                return redirect(url_for('index'))
            
            google = oauth.create_client('google')
            redirect_uri = url_for('google_authorize', _external=True)
            return google.authorize_redirect(redirect_uri)
        except Exception:
            flash("Google login failed. Please try again.", "error")
            return redirect(url_for('login'))
    
    @app.route('/google_authorize')
    def google_authorize():
        try:
            # Get the Google client
            google = oauth.create_client('google')
            # This will fetch the access token and validate the response from Google
            token = google.authorize_access_token()
            # Retrieve user information from Google
            resp = google.get('userinfo')
            user_info = resp.json()
            
            if not user_info:
                flash("Something went wrong.Try again later", "error")
                return redirect(url_for('login'))

            # Use the email as a unique identifier – adjust as needed
            user = User.query.filter_by(email=user_info.get('email')).first()
            if not user:
                # Create a new user if one doesn't exist.
                # If using OAuth, you might not need to store a password.
                user = User(
                    username=user_info.get('name'),
                    email=user_info.get('email'),
                    password=random_password,  # Or store a random string if your model requires a value.
                    role='user'     # Default role – adjust as needed.
                )
                db.session.add(user)
                db.session.commit()

            # Log in the user using Flask-Login
            login_user(user)
            flash("You have been successfully logged in.", "success")
            return redirect(url_for('index'))
        except OAuthError:
            flash("Google authentication was denied. Please try again.", "danger")
        except Exception:
            flash("Google authentication failed. Please try again.", "error")
        return redirect(url_for('login'))
        
    # USING GITHUB ------------------
    @app.route('/github_login')
    def github_login():
        try:
            if current_user.is_authenticated:
                return redirect(url_for('index'))
            github = oauth.create_client('github')
            redirect_uri = url_for('github_authorize',_external=True)
            return github.authorize_redirect(redirect_uri)
        except Exception:
            flash("GitHub authentication failed. Please try again.", "error")
            return redirect(url_for('login'))
   
    @app.route('/github_authorize')
    def github_authorize():
        try:
            # Get the Github client
            github = oauth.create_client('github')
            # This will fetch the access token and validate the response from Google
            token = github.authorize_access_token()
            # Retrieve user information from Google
            resp = github.get('user')
            user_info = resp.json()
            
            if not user_info:
                flash("Something went wrong.Try again later", "error")
                return redirect(url_for('index'))

            # Use the email as a unique identifier – adjust as needed
            user = User.query.filter_by(email=user_info.get('email')).first()
            if not user:
                # Create a new user if one doesn't exist.
                # If using OAuth, you might not need to store a password.
                user = User(
                    username=user_info.get('name'),
                    email=user_info.get('email'),
                    password=random_password,  # Or store a random string if your model requires a value.
                    role='user'     # Default role – adjust as needed.
                )
                db.session.add(user)
                db.session.commit()

            # Log in the user using Flask-Login
            login_user(user)
            flash("You have been successfully logged in.", "success")
            return redirect(url_for('index'))
        except OAuthError:
            flash("GitHub authentication was denied. Please try again.", "error")
        except Exception:
            flash("GitHub authentication failed. Please try again.", "error")
        return redirect(url_for('index'))

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:  # Prevent logged-in users from accessing signup
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("User already registered, please login.", "danger")
                return render_template('signup.html')

            hashed_password = bcrypt.generate_password_hash(password)
            new_user = User(username=username,email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash("Signup successful, please login.", "success")
            return redirect(url_for('login'))

        return render_template('signup.html')

    @app.route('/login', methods=['GET','POST'])
    def login():
        if current_user.is_authenticated:  # Preventing logged-in users from accessing login
            return redirect(url_for('index'))
        if request.method == 'POST':
            password = request.form.get('password')
            email = request.form.get('email')

            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid email or password", "danger")
                return redirect(url_for('login'))

        return render_template('login.html')
    
    @app.route('/logout')
    @login_required  
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.template_filter('format_date')
    def format_date(value, format='%b %d, %Y, %I:%M %p'):
        if value:
           return value.strftime(format)
        return 'N/A'
 
    @app.route('/manage_users')
    @login_required
    def manage_users():
        if hasattr(current_user, 'role') and current_user.role in ['admin']:
            users = User.query.all()
            return render_template('manage_users.html', users=users)
        else:
            return redirect(url_for('index'))

    @app.route('/add_course', methods=['GET', 'POST'])
    @login_required
    def add_course():
        if hasattr(current_user, 'role') and current_user.role in ['admin', 'subadmin']:
            if request.method == 'POST':
                course_name = request.form.get('course_name')
                description = request.form.get('description')
                price = request.form.get('price')
                course_image_file = request.files.get('course_image')
                image_path = None

                print("img path", course_image_file)

                # Check if file is uploaded and is of valid type
                if course_image_file and allowed_file(course_image_file.filename):
                    filename = secure_filename(course_image_file.filename)
                    file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Full static path
                    print("Saving image to:", file_save_path)  # Debugging log
                    
                    # Save file
                    course_image_file.save(file_save_path)

                    # Store **relative path** (for Flask `static/` access)
                    image_path = f'uploads/{filename}'

                new_course = Course(
                    course_name=course_name,
                    description=description,
                    price=price,
                    course_image=image_path
                )
                db.session.add(new_course)
                db.session.commit()
                flash(f"Course: {course_name} added successfully!", "success")
                return redirect(url_for('index'))
            
            return render_template('add_course.html')
        else:
            return redirect(url_for('index'))
    
    @app.route('/view_course/<id>')
    @login_required
    def view_course(id):
        course = Course.query.get_or_404(id)
        return render_template('view_course.html', course=course)

    @app.route('/delete/<id>', methods=['DELETE'])
    @login_required
    def delete(id):
        if hasattr(current_user, 'role') and current_user.role in ['admin']:
            course = Course.query.get_or_404(id)
            db.session.delete(course)
            
            db.session.commit()
            flash("Course deleted successfully!", "success")
            
            return jsonify({'redirect': url_for('index')})
        else:
            return jsonify({'redirect': url_for('index')})

    @app.route('/edit/<id>', methods=['GET', 'POST'])
    @login_required
    def edit(id):
        if hasattr(current_user, 'role') and current_user.role in ['admin', 'subadmin']:
            course = Course.query.get_or_404(id)
            if request.method == 'POST':
                # Update course using form data
                course.course_name = request.form['course_name']
                course.description = request.form['description']
                course.price = float(request.form['price'])
                
                course_image_file = request.files.get('course_image')
                print("IMAGE::", course_image_file)
                if course_image_file and allowed_file(course_image_file.filename):
                    filename = secure_filename(course_image_file.filename)
                    file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    course_image_file.save(file_save_path)
                    # Update the course_image field with the relative path for static access
                    course.course_image = f'uploads/{filename}'

                db.session.commit()
                flash("Course updated successfully!", "success")
                return redirect(url_for('index'))
            else:
                # GET request returns JSON with current course details
                return jsonify({
                    'course_name': course.course_name,
                    'description': course.description,
                    'price': float(course.price),
                    'course_image': course.course_image
                })
        else:
            return redirect(url_for('index'))
            
    @app.route("/create_checkout_session/<id>", methods=['GET'])
    @login_required 
    def create_checkout_session(id):
        course = Course.query.get_or_404(id)
        if not course:
            flash("Course not found!", "error")
            return redirect(url_for('index'))

        # Check if the user has already purchased the course
        existing_purchase = Purchase.query.filter_by(user_id=current_user.uid, course_id=id).first()
        if existing_purchase:
            flash("You have already purchased this course.", "info")
            return redirect(url_for('my_learning'))

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=current_user.email,
                billing_address_collection='auto',
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {'name': course.course_name},
                            'unit_amount': int(round(course.price * 100)),
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                metadata={
                    'course_id': id,
                    'user_id': current_user.uid
                },
                success_url=url_for('success', course_id=id, _external=True),
                cancel_url=url_for('failure', _external=True)
            )
            return redirect(checkout_session.url, code=303)

        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for('index'))
    

    # @app.route('/webhook', methods=['POST'])
    # def webhook():
    #     payload = request.data
    #     sig_header = request.headers.get('Stripe-Signature')

    #     try:
    #         # Verify the event came from Stripe
    #         event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    #     except ValueError as e:
    #         # Invalid payload
    #         print("⚠️  Webhook error while parsing basic request: " + str(e))
    #         return jsonify(success=False), 400
    #     except stripe.error.SignatureVerificationError as e:
    #         # Invalid signature
    #         print("⚠️  Webhook signature verification failed: " + str(e))
    #         return jsonify(success=False), 400

    #     # Handle the event
    #     if event['type'] == 'checkout.session.completed':
    #         session = event['data']['object']
    #         metadata = session.get('metadata', {})
    #         course_id = metadata.get('course_id')
    #         user_id = metadata.get('user_id')
    #         print(f"Payment succeeded for user {user_id} and course {course_id}. Amount: {session.get('amount_total')}")

    #         # Check for duplicate purchase
    #         existing_purchase = Purchase.query.filter_by(user_id=user_id, course_id=course_id).first()
    #         if not existing_purchase:
    #             new_purchase = Purchase(
    #                 user_id=user_id,
    #                 course_id=course_id
    #             )
    #             db.session.add(new_purchase)
    #             db.session.commit()
    #         else:
    #             print("Purchase already recorded.")

    #     elif event['type'] == 'payment_method.attached':
    #         payment_method = event['data']['object']
    #         print('Payment method attached:', payment_method['id'])
    #     else:
    #         print('Unhandled event type {}'.format(event['type']))

    #     return jsonify(success=True), 200
    
    # @app.route("/success/<course_id>")
    # @login_required
    # def success(course_id):
    #     flash("Payment successful! Course added to My Learning.", "success")
    #     return redirect(url_for('my_learning'))

    @app.route("/success/<course_id>")
    @login_required
    def success(course_id):
        existing_purchase = Purchase.query.filter_by(user_id=current_user.uid, course_id=course_id).first()
        if existing_purchase:
            flash("You have already purchased this course.", "info")
        else:
            new_purchase = Purchase(
                user_id=current_user.uid,
                course_id=course_id,
            )
            db.session.add(new_purchase)
            db.session.commit()
            flash("Payment successful! Course added to My Learning.", "success")
        
        return redirect(url_for('my_learning'))

    @app.route("/failure")
    @login_required
    def failure():
        flash("Payment failed or was canceled. Please try again.", "error")
        return redirect(request.referrer or url_for('index'))
    
    @app.route("/my-learning")
    @login_required
    def my_learning():
        purchases = Purchase.query.filter_by(user_id=current_user.uid).all()
        courses = []
        for purchase in purchases:
            course = purchase.course
            courses.append({
                "id": course.id,
                "course_name": course.course_name,
                "course_image": course.course_image,
                "description": course.description,
            })
        return render_template("my_learning.html", courses=courses)






