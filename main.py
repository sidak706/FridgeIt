from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask import Flask, request, jsonify
import google.generativeai as genai
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

# Initialize extensions after configuration
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Database model for the User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='owner', lazy=True)  # Relationship with Item model


# Database model for the Item
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    item_description = db.Column(db.String(200), nullable=True)
    expiry = db.Column(db.DateTime, nullable=True)

    


# Registration Form
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    email = StringField(validators=[InputRequired(), Length(min=8, max=100)], render_kw={"placeholder": "Email"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')


# Login Form
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_items = Item.query.filter_by(user_id=current_user.id).all()  # Retrieve items for the current user
    return render_template('dashboard.html', email=current_user.email, user_items=user_items)

@app.route('/list', methods=['GET', 'POST'])
# @login_required
def showList():
    return render_template("list.html")

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Decode hash
        new_user = User(username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/addItem', methods=['POST'])
@login_required
def addItem():
    data = request.get_json()
    # item_name = data
    item_name = data['itemData']['name']  # Extract the actual item name
    # item_name = data.get('item_name')  # Extract 'item_name' from JSON
    print(item_name)
    user_id = current_user.id  # Use the logged-in user's ID

    if not item_name:
        return jsonify({'error': 'Missing item name'}), 400

    print(f"{item_name}: {getExpiry(item_name)}")
    expiry = datetime.now() + timedelta((int) (getExpiry(item_name)))
    # # Create and save the new item in the database
    new_item = Item(user_id=user_id, item_name=item_name, expiry = expiry)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({'message': 'Item added successfully!', 'item': {'user_id': user_id, 'name': item_name, 'expiry': expiry}})


@app.route('/emailList', methods=['GET'])
@login_required
def emailList():
    all_items = Item.query.all()
    # for item in all_items:
    #     print(f"ITEM: {item.expiry}")
    try:
        print(all_items)
        emailAll(current_user.email, all_items)
        return jsonify({'message': 'Email sent successfully!'})
    except Exception as e:
        return jsonify({'Could not send email'})
        

@app.route('/clearList', methods=['GET'])
@login_required
def clearList():
    try:
        # Delete all items from the Item table
        db.session.query(Item).delete()
        db.session.commit()
        print("All items deleted successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error deleting items: {e}")
    return jsonify({'message': 'Items deleted successfully!'})

    


def getExpiry(name):
    genai.configure(api_key="AIzaSyB_44dv2A-soBHojY4AzayMR5lTvdIeKqY")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"""Give an estimate for how many days/months it
                                       takes for {name} to expire in the fridge? GIVE the answer in a format
                                       where the first part of your response is 1 if your suggestion is months
                                       0 otherwise. The second part of your response should be the actual days/months
                                       value. For example, if your answer is 3 months, your response should be
                                       1 3 , if its 2 days, it should be 1 2. Do not include hyphenated numbers in your
                                       response, if your answer is 2-3 days, just say 0 2, i.e only give the lower bound. 
                                       If you think the dish name is invalid, your response should be -1.""")
    print(response.text)
    if( ((int) (response.text[0])) == 1):
        return (int) (response.text[2]) * 30

    else: return response.text[2]


def emailAll(userEmail, all_items): 
    # Configuration for SendGrid
    smtp_server = "smtp.sendgrid.net"
    port = 587  # TLS port
    username = "apikey"  # The username is always 'apikey' for SendGrid

    password = os.getenv("SENDGRID_API_KEY")
    sender_email = "fridgeit720@gmail.com"
    receiver_email = userEmail

    # Create the email subject and body
    subject = "Your Fridge Items and Expiry Details"
    body = "Here are the items in your fridge along with their expiry details:\n\n"
    
    # Append all items to the body
    for item in all_items:
        body += f"- {item.item_name} (Expiry: {item.expiry})\n"

    body += "\nPlease ensure to use these items before expiry to reduce waste. Happy Cooking!\n\nFridgeIt Team"

    # Create MIMEText object for the body and a MIMEMultipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach the body to the message
    message.attach(MIMEText(body, "plain"))

    # Sending email through SendGrid SMTP
    try:
        # Connect to the server
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Secure the connection using TLS
            server.login(username, password)  # Log in with the SendGrid API key
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")



def send_email(userEmail, food, time_left, fridge, expired):
    # Configuration for SendGrid
    smtp_server = "smtp.sendgrid.net"
    port = 587  # TLS port (you could also use port 465 for SSL)
    username = "apikey"  # The username is always 'apikey' for SendGrid
    # password = "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"  # Your API Key
    password = "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"
    sender_email = "fridgeit720@gmail.com"
    receiver_email = userEmail
    # Create the email
    subject = ""
    body = """
    Dish approaching Expiry
    """

    if(expired): 
        subject = "Expired dish notification"
        body = f""" The following dish has expired:
                    Name: {food}
                    Place: {fridge if fridge == 1 else "freezer"}
                """
    else: 
        subject = "Dish expiry approaching"
        body = f""" The following expires soon:
                    Name: {food}
                    Place: {fridge if fridge == 1 else "freezer"}
                    Estimated expiry: {time_left}
                """

    
    # Create MIMEText object for the body and a MIMEMultipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject


    # Attach the body to the message
    message.attach(MIMEText(body, "plain"))

    # Sending email through SendGrid SMTP
    try:
        # Connect to the server
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Secure the connection using TLS
            server.login(username, password)  # Log in with the SendGrid API key
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")



if __name__ == "__main__":
    # To initialize the database
    with app.app_context():
        db.create_all()

    app.run(debug=True)
