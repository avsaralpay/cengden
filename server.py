#cengden server.py dosyası
#MongoDB url = mongodb+srv://aavsaralpay:<password>@cluster0.khgwljs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
from flask import Flask,render_template,url_for,request,session,redirect
from flask_pymongo import PyMongo
import bcrypt
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['MONGO_DBNAME'] = 'cengden'
app.config['MONGO_URI'] = 'mongodb+srv://aavsaralpay:Alpicik123.@cluster0.khgwljs.mongodb.net/cengden?retryWrites=true&w=majority&appName=Cluster0'

mongo = PyMongo(app)


def send_verification_email(email_to, name,verification_code):
    message = Mail(
        from_email='aavsaralpay@gmail.com',
        to_emails=email_to,
        subject='Verify your CENGden account',
        html_content=f'<strong>Hello {name},</strong><br>Your verification code is: <strong>{verification_code}</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/verify', methods=['POST'])
def verify():
    temp_verifications = mongo.db.temp_verifications
    users = mongo.db.users

    email = request.form.get('email')
    submitted_code = request.form.get('verification_code')
    temp_user = temp_verifications.find_one({'email': email})

    if temp_user and temp_user['verification_code'] == submitted_code:
        temp_user.pop('_id', None)  
        temp_user.pop('verification_code', None)  
        users.insert_one(temp_user)
        
        temp_verifications.delete_one({'email': email})
        
        session['email'] = email 
        return redirect(url_for('index'))
    else:
        error_message = 'Invalid verification code!'
        return render_template('verify.html', error=error_message, email=email)

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    per_page = 5  # Number of items per page
    total_items = mongo.db.items.count_documents({'active': True})
    total_pages = (total_items + per_page - 1) // per_page
    items = mongo.db.items.find({'active': True}).sort("timestamp", -1).skip((page - 1) * per_page).limit(per_page)
    return render_template('index.html', items=list(items), myitems=False, page=page, total_pages=total_pages)


@app.route('/items')
def my_items():
    items = mongo.db.items.find({'user_email': session['email']}).sort("timestamp", -1)
    return render_template('index.html', items=list(items), myitems=True)

@app.route('/favorites')
def favorites():
    if 'email' not in session:
        return redirect(url_for('login')) 

    user = mongo.db.users.find_one({'email': session['email']})
    favorite_ids = user.get('favorites', [])
    favorite_object_ids = [ObjectId(id) for id in favorite_ids]
    favorite_items = mongo.db.items.find({'_id': {'$in': favorite_object_ids}})

    return render_template('index.html', items=list(favorite_items), viewing_favorites=True)

@app.route('/delete_item/<item_id>')
def delete_item(item_id):
    if 'email' not in session:
        return redirect(url_for('login'))  

    item = mongo.db.items.find_one({'_id': ObjectId(item_id)})

    if item and session['email'] == item.get('user_email'):
        mongo.db.users.update_many({}, {'$pull': {'favorites': ObjectId(item_id)}})
        mongo.db.items.delete_one({'_id': ObjectId(item_id)})

    return redirect(url_for('index')) 

@app.route('/category/<category_name>')
def category(category_name):
    page = request.args.get('page', 1, type=int)
    per_page = 5  
    offset = (page - 1) * per_page

    total_items = mongo.db.items.count_documents({'category': category_name, 'active': True})
    total_pages = (total_items + per_page - 1) // per_page 
    
    items = mongo.db.items.find({'category': category_name, 'active': True}).skip(offset).limit(per_page).sort([('timestamp', -1)])

    return render_template('category.html', items=list(items), category=category_name, current_page=page, total_pages=total_pages)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        users = mongo.db.users
        email = request.form.get('email')  
        login_user = users.find_one({'email': email})
        user_role = login_user.get('role') if login_user else None
        if login_user and bcrypt.checkpw(request.form.get('pass').encode('utf-8'), login_user['password']):
            session['email'] = email
            session['role'] = user_role
            return redirect(url_for('index'))
        else:
            error_message = 'Invalid email or password'
            return render_template('login.html', error=error_message)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)  
    return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        temp_verifications = mongo.db.temp_verifications  
        email = request.form['email']  
        if not email.endswith('@ceng.metu.edu.tr'):
            error_message = 'Registration is only allowed for CENG emails.'
            return render_template('register.html', error=error_message)
        
        existing_user = users.find_one({'email': email})

        if existing_user is None:
            verification_code = generate_verification_code()
            existing_temp_user = temp_verifications.find_one({'email': email})
            if existing_temp_user:
                temp_verifications.update_one(
                    {'email': email},
                    {'$set': {'verification_code': verification_code}}
                )
            else:
                temp_verifications  .insert_one({
                    'email': email,
                    'verification_code': verification_code,
                    'name': request.form['name'],
                    'phone': request.form['phone'],
                    'password': bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt()),
                    'role': 'authenticated_user',
                    'favorites': []
                })
            send_verification_email(email, request.form['name'], verification_code)
            session['email'] = email  
            return render_template('verify.html', email=email)
        
        error_message = 'That email already exists!'
        return render_template('register.html', error=error_message)

    return render_template('register.html')


@app.route('/add_or_update_item',methods=['POST','GET'], defaults={'item_id': None})
@app.route('/add_or_update_item/<item_id>', methods=['POST','GET'])
def add_or_update_item(item_id=None):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    is_update = bool(item_id)  
    item_data = {}  
    old_price = None
    if item_id:
        item = mongo.db.items.find_one({'_id': ObjectId(item_id), 'user_email': session['email']})
        old_price = float(item['price']) if 'price' in item else None
        print(old_price)
        if not item:
            return redirect(url_for('index'))  
    else:
        item = None 

    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title', '').strip()
        price = request.form.get('price', '').strip()
        description = request.form.get('description', '').strip()
        image_link = request.form.get('image_link', '').strip()
        
        item_data = {
            'category': category,
            'user_email': session['email'],
            'title': title,
            'price': price,
            'description': description,
            'timestamp': datetime.utcnow(),
            'active': True  
        }
        new_price = float(price) if price else None
        print(new_price)
        if old_price and new_price and new_price < old_price:
            print('Price drop detected!')
            notify_price_drop(item_id, old_price, new_price)
        if image_link:
            item_data['image_link'] = image_link
        else:
            item_data['image_link'] = 'https://via.placeholder.com/300x200.png?text=No+Image'
        category_fields = {
            'vehicles': ['type', 'brand', 'model', 'year', 'color', 'engine_displacement', 'fuel_type', 'transmission_type', 'mileage'],
            'phones': ['brand', 'model', 'year', 'operating_system', 'processor', 'ram', 'storage', 'battery_capacity'],
            'computers': ['type', 'brand', 'model', 'year', 'processor', 'ram','graphics_card', 'operating_system'],
            'lessons': ['tutor_name','location','duration']
        }

        for field in category_fields.get(category, []):
            field_value = request.form.get(field, '').strip()
            if field_value:
                item_data[field] = field_value

        if category == 'vehicles':
            additional_attribute_keys = request.form.getlist('additional_attribute_keys[]')
            additional_attribute_values = request.form.getlist('additional_attribute_values[]')
            additional_attributes = {key: value for key, value in zip(additional_attribute_keys, additional_attribute_values) if key and value}
            if additional_attributes:
                item_data['additional_attributes'] = additional_attributes

        if category == 'phones':
            camera_specs = [{'Type': t.strip(), 'MP': mp.strip()} for t, mp in zip(request.form.getlist('camera_specs_type[]'), request.form.getlist('camera_specs_mp[]')) if t.strip() and mp.strip()]
            if camera_specs:
                item_data['camera_specifications'] = camera_specs

        if category == 'lessons':
            lesson_topics = request.form.getlist('lessons[]')  
            clean_lesson_topics = [topic.strip() for topic in lesson_topics if topic.strip()] 

            if clean_lesson_topics:
                item_data['lessons'] = clean_lesson_topics

        if category == 'computers':
            computer_storages = [{'Type': t.strip(), 'Size': s.strip()} for t, s in zip(request.form.getlist('Storage_specs_type[]'), request.form.getlist('Storage_specs_size[]')) if t.strip() and s.strip()]
            if computer_storages:
                item_data['storage_computers'] = computer_storages

        if item_id:
            mongo.db.items.update_one({'_id': ObjectId(item_id)}, {'$set': item_data})
        else:
            mongo.db.items.insert_one(item_data)
        return redirect(url_for('index'))
    else:
        return render_template('additem.html', item=item, is_update=is_update)
 
def notify_price_drop(item_id, old_price, new_price):
    users = mongo.db.users.find({'favorites': ObjectId(item_id)})
    for user in users:
        send_price_drop_email(user['email'], old_price, new_price)

def send_price_drop_email(email_to, old_price, new_price):
    subject = "About Your favourite item"
    html_content = f"""
    <p>Hello,</p>
    <p>One of your favorited items has dropped in price from {old_price} to {new_price}.</p>
    <p>Visit CENGden to check it out!</p>"""
    message = Mail(
        from_email='aavsaralpay@gmail.com',
        to_emails=email_to,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent to {email_to} - Status Code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email to {email_to} - Error: {str(e)}")

@app.route('/item/<item_id>')
def item_detail(item_id):
    item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
    user_info = None
    if 'email' in session and item: 
        post_user = mongo.db.users.find_one({'email': item['user_email']})
        if post_user:  
            user_info = {'email': post_user['email'], 'phone': post_user.get('phone', 'Phone not provided')}
    is_favorite = False
    if 'email' in session:
        logged_in_user = mongo.db.users.find_one({'email': session['email']})
        if logged_in_user and item:
            is_favorite = ObjectId(item_id) in logged_in_user.get('favorites', [])
    return render_template('item_detail.html', item=item, user=user_info, is_favorite=is_favorite)



@app.route('/deactivate_item/<item_id>')
def deactivate_item(item_id):
    if 'email' not in session:
        return redirect(url_for('login'))  

    mongo.db.items.update_one(
        {'_id': ObjectId(item_id), 'user_email': session['email']},
        {'$set': {'active': False}}
    )
    return redirect(url_for('index'))

@app.route('/activate_item/<item_id>')
def activate_item(item_id):
    if 'email' not in session:
        return redirect(url_for('login'))  

    mongo.db.items.update_one(
        {'_id': ObjectId(item_id), 'user_email': session['email']},
        {'$set': {'active': True}}
    )
    return redirect(url_for('index'))

@app.route('/add_to_favorites/<item_id>', methods=['POST'])
def add_to_favorites(item_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    mongo.db.users.update_one(
        {'email': session['email']},
        {'$addToSet': {'favorites': ObjectId(item_id)}}
    )
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/remove_from_favorites/<item_id>', methods=['POST'])
def remove_from_favorites(item_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    mongo.db.users.update_one(
        {'email': session['email']},
        {'$pull': {'favorites': ObjectId(item_id)}}
    )
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'email' not in session:
        return redirect(url_for('login'))

    users = mongo.db.users
    user = users.find_one({'email': session['email']})

    if request.method == 'POST':
        new_email = request.form.get('email')

        new_phone = request.form.get('phone')
        update_data = {}

        if new_email and new_email != session['email']:
            update_data['email'] = new_email
            session['email'] = new_email  
            items = mongo.db.items
            items.update_many({'user_email': user['email']}, {'$set': {'user_email': new_email}})

        if new_phone and new_phone != user.get('phone'):
            update_data['phone'] = new_phone

        if update_data:
            users.update_one({'email': user['email']}, {'$set': update_data})

        return redirect(url_for('index'))

    return render_template('account.html', user=user)


@app.route('/admin')
def admin_panel():
    if 'email' not in session or 'role' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'admin':
        return "You do not have access to this page", 403 
    
    users = mongo.db.users.find({})
    items = mongo.db.items.find({})
    return render_template('admin_panel.html', users=users, items=items)

@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    if 'email' not in session or 'role' not in session or session['role'] != 'admin':
        return "Unauthorized", 403
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user:  
        items = mongo.db.items.find({'user_email': user['email']})
        item_ids = [item['_id'] for item in items]

        mongo.db.users.update_many({}, {'$pull': {'favorites': {'$in': item_ids}}})

        mongo.db.items.delete_many({'user_email': user['email']})
        mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('admin_panel'))

@app.route('/delete_item_admin/<item_id>')
def delete_item_admin(item_id):
    if 'email' not in session or 'role' not in session or session['role'] != 'admin':
        return "Unauthorized", 403
    
    mongo.db.users.update_many({}, {'$pull': {'favorites': ObjectId(item_id)}})
    mongo.db.items.delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('admin_panel'))

if __name__ == "__main__":
    app.secret_key = 'secret_key'
    app.run(debug=True)
