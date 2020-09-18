
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.hotel import HotelModel

class Hoteis(Resource):
	def get(self):
		return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]}

class Hotel(Resource):
	argumentos = reqparse.RequestParser()
	argumentos.add_argument('nome',
		type=str,
		required=True,
		help="The field 'nome' cannot be left blank.")

	argumentos.add_argument('estrelas',
		type=float,
		required=True,
		help="The field 'estrelas' cannot be left blank.")

	argumentos.add_argument('diaria')
	argumentos.add_argument('cidade')

	def get(self, hotel_id):
		hotel = HotelModel.find_hotel(hotel_id)
		if hotel:
			return hotel.json()

		return {'message': 'HOTEL NOT FOUND'}, 404

	@jwt_required
	def post(self, hotel_id):
		if HotelModel.find_hotel(hotel_id):
			return {'message': "HOTEL ID '{}' ALREADY EXISTS.".format(hotel_id)}, 404

		dados = Hotel.argumentos.parse_args()
		hotel = HotelModel(hotel_id, **dados)#.json()
		try:
			hotel.save_hotel()
		except:
			return {'message': 'An internal error ocurred while trying to save hotel.'}, 500		

		return hotel.json(), 200

	@jwt_required
	def put(self, hotel_id):
		dados = Hotel.argumentos.parse_args()
		hotel = HotelModel.find_hotel(hotel_id)
		
		if hotel:
			hotel.update_hotel(**dados)
			hotel.save_hotel()
			return hotel.json(), 200

		hotel = HotelModel(hotel_id, **dados)
		try:
			hotel.save_hotel()
		except:
			return {'message': 'An internal error ocurred while trying to save hotel.'}, 500		

		return hotel.json(), 201

	@jwt_required
	def delete(self, hotel_id):
		hotel = HotelModel.find_hotel(hotel_id)
		if hotel:
			try:
				hotel.delete_hotel()
			except:
				return {'message': 'An internal error ocurred while trying to delete hotel.'}, 500		

			return {'message': 'HOTEL DELETED.'}

		return {'message': 'HOTEL NOT FOUND.'}
