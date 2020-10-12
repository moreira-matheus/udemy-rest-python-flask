
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp

from models.usuario import UserModel
from blacklist import BLACKLIST

atributos = reqparse.RequestParser()
atributos.add_argument('login',
	type=str, required=True,
	help="The field 'login' cannot be left blank.")
atributos.add_argument('senha',
	type=str, required=True,
	help="The field 'senha' cannot be left blank.")
		
class User(Resource):
	# /usuarios/{user_id}
	def get(self, user_id):
		user = UserModel.find_user(user_id)
		if user:
			return user.json()

		return {'message': 'USER NOT FOUND'}, 404

	@jwt_required
	def delete(self, user_id):
		user = UserModel.find_user(user_id)
		if user:
			try:
				user.delete_user()
			except:
				return {'message': 'An internal error ocurred while trying to delete user.'}, 500		

			return {'message': 'USER DELETED.'}

		return {'message': 'USER NOT FOUND.'}

class UserRegister(Resource):
	# /cadastro
	def post(self):
		dados = atributos.parse_args()

		if UserModel.find_by_login(dados['login']):
			return {'message': "LOGIN '{}' ALREADY EXISTS.".format(dados['login'])}

		user = UserModel(**dados)
		user.save_user()
		return {'message': 'USER CREATED SUCCESSFULLY.'}, 201

class UserLogin(Resource):

	@classmethod
	def post(cls):
		dados = atributos.parse_args()
		user = UserModel.find_by_login(dados['login'])

		if user and safe_str_cmp(user.senha, dados['senha']):
			token = create_access_token(identity=user.user_id)
			return {'access_token': token}, 200

		return {'message': 'User or password incorrect.'}, 401

class UserLogout(Resource):

	@jwt_required
	def post(self):
		jwt_id = get_raw_jwt()['jti'] # JWT Token Identifier
		BLACKLIST.add(jwt_id)
		return {'message': 'LOGGED OUT SUCCESSFULLY.'}, 200
