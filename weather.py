from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

weather_app = Flask(__name__)
weather_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
weather_db = SQLAlchemy(weather_app)


class Weather(weather_db.Model):
    id = weather_db.Column(weather_db.Integer, primary_key=True)
    city = weather_db.Column(weather_db.String(50), nullable=False)
    date = weather_db.Column(weather_db.String(10), nullable=False)
    max_temp = weather_db.Column(weather_db.Float, nullable=False)
    min_temp = weather_db.Column(weather_db.Float, nullable=False)
    precipitation = weather_db.Column(weather_db.Float, nullable=False)
    sunrise = weather_db.Column(weather_db.String(10), nullable=False)
    sunset = weather_db.Column(weather_db.String(10), nullable=False)

    __table_args__ = (weather_db.UniqueConstraint('city', 'date', name='_city_date_uc'),)


@weather_app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        return redirect(url_for('get_weather', city=city))
    return render_template('index.html')


@weather_app.route('/weather/<city>')
def get_weather(city):
    api_key = 'cbebcb2367854ee28ce122050240509' 
    url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        forecast_data = data['forecast']['forecastday']
        Weather.query.filter_by(city=city).delete()

        for day in forecast_data:
            weather_entry = Weather(
                city=city,
                date=day['date'],
                max_temp=day['day']['maxtemp_c'],
                min_temp=day['day']['mintemp_c'],
                precipitation=day['day']['totalprecip_mm'],
                sunrise=day['astro']['sunrise'],
                sunset=day['astro']['sunset']
            )
            weather_db.session.add(weather_entry)
        weather_db.session.commit()

        return render_template('weather.html', city=city, forecast=forecast_data)

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}", 500


if __name__ == '__main__':
    with weather_app.app_context():
        weather_db.create_all()
    weather_app.run(debug=True)
