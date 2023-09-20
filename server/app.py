#!/usr/bin/env python3
from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe
import traceback
class Signup(Resource):
    def post(self):
        json = request.get_json()
        if (not json.get('username')):
            resp = make_response(
                {'error': '422 Unprocessable Content'},
                422
            )
            return resp

        user = User(
            username=json['username'],
            bio=json['bio'],
            image_url=json['image_url']
        )
        user.password_hash = json['password']
        
        db.session.add(user)
        db.session.commit()
        user_dict = User.query.filter_by(username=user.username).first().to_dict()
        resp = make_response(
            user_dict,
            201
        )
        return resp

class CheckSession(Resource):
    def get(self):
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            resp = make_response(
                user.to_dict(),
                200
            )
            return resp
        else:
            resp = make_response(
                {},
                401
            )
            return resp

class Login(Resource):
    def post(self):
        json = request.get_json()
        user = User.query.filter_by(username=json['username']).first()
        if not user:
            return invalid_login()
        password = json['password']
        if user.authenticate(password):
            session['user_id'] = user.id
            resp = make_response(
                user.to_dict(),
                200
            )
            return resp
        return invalid_login()

def invalid_login():
        resp = make_response(
            {"error": "Invalid username or password"},
            401
        )
        return resp
class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        resp = make_response({}, 401)
        return resp

class RecipeIndex(Resource):
    def get(self):
        if not session['user_id']:
            resp = make_response(
                {},
                401
            )
            return resp
        
        recipes = Recipe.query.filter_by(user_id=session['user_id']).all()
        recipe_dict = [recipe.to_dict() for recipe in recipes]
        resp = make_response(
            recipe_dict,
            200
        )
        return resp
    
    def post(self):
        if not session['user_id']:
            resp = make_response(
                {"message": "User not logged in"},
                401
            )
        json = request.get_json()
        recipe = Recipe(
            title = json['title'],
            instructions = json['instructions'],
            minutes_to_complete = json['minutes_to_complete'],
            user_id = session['user_id']
        )
        try:
            db.session.add(recipe)
            db.session.commit()

            recipe_dict = Recipe.query.order_by(Recipe.id.desc()).first().to_dict()
            resp = make_response(
                recipe_dict,
                201
            )
            return resp
        except IntegrityError as e:
            db.session.rollback()  
            resp = make_response(
                {"message": "Invalid Recipe"},
                422
            )
            return resp
        
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
