import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.hotel import HotelModel

# path /hoteis?cidade=Rio+de+Janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=int)
path_params.add_argument('offset', type=int)


def normalize_path_params(**dados):
    defaults = dict(cidade=None,
                    estrelas_min=0, estrelas_max=5,
                    diaria_min=0, diaria_max=10000,
                    limit=50, offset=0)
    params = {}
    for key in defaults.keys():
        params[key] = dados.get(key, None)\
                      if dados.get(key, None) is not None\
                      else defaults[key]

    if not dados['cidade']:
        _ = params.pop('cidade', None)

    return params

class Hoteis(Resource):
    def get(self):
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()

        dados = path_params.parse_args()
        parametros = normalize_path_params(**dados)
        filtro_cidade = ''

        if parametros.get('cidade', None):
            filtro_cidade = "\nAND cidade LIKE '{}'".format(parametros.pop('cidade'))

        query = """
        SELECT * FROM hoteis
        WHERE (estrelas BETWEEN {estrelas_min} and {estrelas_max})
        AND diaria BETWEEN {diaria_min} and {diaria_max}{filtro_cidade}
        LIMIT {limit} OFFSET {offset}
        """.format(**parametros,filtro_cidade=filtro_cidade)
        result = cursor.execute(query)

        hoteis = []
        for row in result:
            hotel = {'hotel_id': row[0],
                     'nome': row[1],
                     'estrelas': row[2],
                     'diaria': row[3],
                     'cidade': row[4]}
            hoteis.append(hotel)

        return {'hoteis': hoteis}

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
