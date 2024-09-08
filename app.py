#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# Routes

class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([hero.to_dict() for hero in heroes])

class HeroResource(Resource):
    def get(self, hero_id):
        hero = Hero.query.get(hero_id)
        if not hero:
            return {"error": "Hero not found"}, 404
        return jsonify(hero.to_dict())

class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict() for power in powers])

class PowerResource(Resource):
    def get(self, power_id):
        power = Power.query.get(power_id)
        if not power:
            return {"error": "Power not found"}, 404
        return jsonify(power.to_dict())

    def patch(self, power_id):
        power = Power.query.get(power_id)
        if not power:
            return {"error": "Power not found"}, 404
        data = request.get_json()
        description = data.get('description')
        if description:
            try:
                power.description = description
                db.session.commit()
                return jsonify(power.to_dict())
            except ValueError as e:
                return {"errors": [str(e)]}, 400
        return {"errors": ["No valid fields provided"]}, 400

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')
        strength = data.get('strength')

        if not all([hero_id, power_id, strength]):
            return {"errors": ["Missing required fields"]}, 400

        if strength not in ['Strong', 'Weak', 'Average']:
            return {"errors": ["Invalid strength value"]}, 400

        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)

        if not hero or not power:
            return {"errors": ["Hero or Power not found"]}, 404

        hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
        db.session.add(hero_power)
        db.session.commit()

        return jsonify(hero_power.to_dict())

# Add resources to API
api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:hero_id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:power_id>')
api.add_resource(HeroPowerResource, '/hero_powers')

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)
