from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from random import randint
import requests
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    balance: Mapped[float] = mapped_column(db.Float, nullable=False)


def fetch_weather(city):
    geolocator = Nominatim(user_agent="app")
    location = geolocator.geocode(city)
    url = (
        "https://api.open-meteo.com/v1/"
        + f"forecast?latitude={location.latitude}&longitude={location.longitude}&current=temperature_2m"
    )
    result = requests.get(url).json()
    temperature = result["current"]["temperature_2m"]
    return float(temperature)


@app.route("/update_user", methods=["POST"])
def update_user():
    user_id = request.args.get("user_id")
    city = request.args.get("city")
    user = User.query.filter_by(id=user_id).first()
    temperature = fetch_weather(city)
    balance = user.balance
    new_balance = user.balance + temperature
    user.balance += new_balance
    print(temperature,balance,new_balance)
    db.session.commit()
    return jsonify(
        {"username": user.username, "balance": balance, "new_balance": user.balance}
    )


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User(username="1", balance=randint(5000, 15000)))
        db.session.add(User(username="2", balance=randint(5000, 15000)))
        db.session.add(User(username="3", balance=randint(5000, 15000)))
        db.session.add(User(username="4", balance=randint(5000, 15000)))
        db.session.add(User(username="5", balance=randint(5000, 15000)))
        db.session.commit()
    app.run(
        debug=True,
    )
