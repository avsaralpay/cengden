# cengden
E-commerce web application based on cloud services
Author : Alpay Avşar 
Student id : 2171254

# CENGden Server Functionality

## Functions and Routes

- `send_verification_email(email_to, name, verification_code)`: Sends a verification email to the user with a unique code for account verification.

- `generate_verification_code(length)`: Generates a random alphanumeric string used as a verification code for new user registration.

- `@app.route('/verify', methods=['POST'])`: Processes user verification by comparing input codes with the stored verification codes and if verified registers user to database.

- `@app.route('/')`: The homepage route that parses index.html and displays latest items.

- `@app.route('/items')`: Displays items posted by the currently logged-in user.

- `@app.route('/favorites')`: Shows the favorited items of the logged-in user.

- `@app.route('/delete_item/<item_id>')`: Allows the logged-in user to delete an item they posted.

- `@app.route('/category/<category_name>')`: Displays items filtered by the selected category.

- `@app.route('/login', methods=['GET', 'POST'])`: Handles the user login process.

- `@app.route('/logout')`: Logs out the current user and clears their session.

- `@app.route('/register', methods=['POST', 'GET'])`: Manages the registration process for new users.

- `@app.route('/add_or_update_item', methods=['POST', 'GET'], defaults={'item_id': None})`: Allows users to add new items or update existing ones.

- `notify_price_drop(item_id, old_price, new_price)`: Sends an email notification to users who favorited an item if its price drops.

- `send_price_drop_email(email_to, old_price, new_price)`: Constructs and sends the price drop notification email.

- `@app.route('/item/<item_id>')`: Displays the details of a specific item.

- `@app.route('/deactivate_item/<item_id>')`: Deactivates a listed item by the owner.

- `@app.route('/activate_item/<item_id>')`: Reactivates a deactivated item by the owner.

- `@app.route('/add_to_favorites/<item_id>', methods=['POST'])`: Allows users to add an item to their favorites.

- `@app.route('/remove_from_favorites/<item_id>', methods=['POST'])`: Allows users to remove an item from their favorites.

- `@app.route('/account', methods=['GET', 'POST'])`: Enables users to view and update their account information.

- `@app.route('/admin')`: Admin panel showing all users and items, allowing admin actions such as delete item or user.

- `@app.route('/delete_user/<user_id>')`: Allows the admin to delete a user and their items.

- `@app.route('/delete_item_admin/<item_id>')`: Allows the admin to delete any item.

## Additional Information

The application uses Flask for the backend, PyMongo for interacting with the MongoDB database, bcrypt for password hashing, and SendGrid for sending emails.

I registered e1111111@ceng.metu.edu.tr as admin and one can sign in entering password 11111111
I registered e2222222@ceng.metu.edu.tr as authenticated user and one can sign in entering password 22222222
User can update/delete/reactivate and deactivate theirs posts through my items page.
User can add an item through add item page.
User can add item to favorites in item detail page, display favourited items through my favorites page.
User can update account setting in my account page.
Admins can delete users/items through admin panel page.


