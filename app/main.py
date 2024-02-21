from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask.views import MethodView
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from random import randint
import requests
from geopy.geocoders import Nominatim
import redis.asyncio as redis
from contextlib import asynccontextmanager
from geopy.adapters import AioHTTPAdapter
from geopy.exc import GeocoderTimedOut,GeocoderRateLimited

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"


@asynccontextmanager
async def get_clinet():
    pool = redis.ConnectionPool.from_url("redis://redis:6379")
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.aclose()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    balance: Mapped[float] = mapped_column(db.Float, nullable=False)


async def check_key_existence(key):
    async with get_clinet() as redis:
        result = await redis.exists(key)
    return result


async def get_city_data(city):
    async with Nominatim(
        user_agent="app",
        adapter_factory=AioHTTPAdapter,
        timeout=10
    ) as geolocator:
        location = await geolocator.geocode("city")
    return location.latitude, location.longitude


async def fetch_weather(city):
    latitude, longitude = await get_city_data(city)
    url = (
        "https://api.open-meteo.com/v1/"
        + f"forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"
    )
    result = requests.get(url).json()
    temperature = result["current"]["temperature_2m"]
    return float(temperature)


class UpdateUserView(MethodView):
    async def post(self):
        user_id = request.args.get("user_id")
        city = request.args.get("city")
        user = User.query.filter_by(id=user_id).first()
        async with get_clinet() as redis:
            if not await check_key_existence(city):
                try:
                    temperature = await fetch_weather(city)
                    await redis.setex(name=city,time=600, value=temperature)
                except GeocoderTimedOut:
                    return {"detail":"Service unavaliable"}, 400
                except GeocoderRateLimited:
                    return {"detail": "Rate limit on Nominatim"}, 400
            if not await check_key_existence(user_id):
                await redis.setex(name=user_id, time=600, value=user.balance)
            balance = await redis.get(user_id)
            temperature = await redis.get(city)
            balance = float(balance)
            temperature = float(temperature)
            new_balance = balance + temperature
            await redis.setex(name=user_id, time=600, value=new_balance)
            if new_balance < 0:
                return {"detail": "User balance cant be zero"}, 400
            user.balance = new_balance
            db.session.commit()
        return (
            jsonify(
                {
                    "username": user.username,
                    "balance": balance,
                    "new_balance": user.balance,
                }
            ),
            200,
        )


update_user_view = UpdateUserView.as_view("update_user")
app.add_url_rule("/update_user", view_func=update_user_view, methods=["POST"])

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User(username="1", balance=randint(5000, 15000)))
        db.session.add(User(username="2", balance=randint(5000, 15000)))
        db.session.add(User(username="3", balance=randint(5000, 15000)))
        db.session.add(User(username="4", balance=randint(5000, 15000)))
        db.session.add(User(username="5", balance=randint(5000, 15000)))
        db.session.add(User(username="6", balance=0))
        db.session.commit()
    app.run(debug=True, host="0.0.0.0", port="5000")
