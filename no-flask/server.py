import mysql.connector
from mysql.connector import errorcode
from aiohttp import web
import json
import datetime
import re


def validateCPF(cpf: str) -> bool:

    # Verifica a formatação do CPF
    if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
        return False

    # Obtém apenas os números do CPF, ignorando pontuações
    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    # Verifica se o CPF possui 11 números ou se todos são iguais:
    if len(numbers) != 11 or len(set(numbers)) == 1:
        return False

            # Validação do primeiro dígito verificador:
    sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        return False

    # Validação do segundo dígito verificador:
    sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        return False

    return True


class Users:

    table_name = 'pessoas'

    def remove(self, uid):
        query = 'DELETE FROM {} WHERE id_pessoa = {}'.format(self.table_name, uid)
        cur =  db.setQuery(query).execute()
        db.commit()
        return cur
        
    def add(self, args):
        query = "INSERT INTO {} (`nome`,`rg`, `cpf`,`data_nascimento`, `data_admissao`) VALUES ('{}', '{}','{}', '{}','{}')".format(self.table_name, args["nome"], args["rg"], args["cpf"], args["data_nascimento"], args["data_admissao"])
        # print(query)
        cursor = db.setQuery(query).execute()
        db.commit()
        return cursor


    def getAll(self):
        query = 'SELECT id_pessoa, nome, data_admissao FROM {} WHERE 1'.format(self.table_name)
        return db.setQuery(query).execute()

    def getOne(self, uid):
        query = 'SELECT id_pessoa, nome, data_admissao FROM {} WHERE id_pessoa = {}'.format(self.table_name, uid)
        return db.setQuery(query).execute().fetchone()

    def getOneBy(self, key, value):
        query = "SELECT id_pessoa, nome, data_admissao FROM {} WHERE {} = '{}'".format(self.table_name, key, value)
        return db.setQuery(query).execute().fetchone()


class Database:

    def __init__(self):
        self.user     = 'nicolasbortoluzzi'
        self.password = 'bmljb2xhc2Jv'
        self.host     = 'jobs.visie.com.br'
        self.database = 'nicolasbortoluzzi'

        self.query    = ""


    def setQuery(self, query):
        self.query = query
        return self


    def execute(self):
        if (len(self.query) <= 0):
            raise Exception("Query string empty")
        
        self.cursor.execute(self.query)
        return self.cursor

    
    def commit(self):
        self.con.commit()


    def connect(self):
        try:
            self.con = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
            self.cursor = self.con.cursor(buffered=True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    
    def disconnect(self):
        self.con.close()



db = Database()
db.connect()

users = Users()

async def get_users(request):
    user    = users.getAll()
    pessoas = []

    for (id_pessoa, nome, data_admissao) in user:
        pessoas.append({
            "id_pessoa": id_pessoa,
            "nome": nome,
            "data_admissao": data_admissao.isoformat()
        })

    return web.Response(text=json.dumps(pessoas), headers={'Access-Control-Allow-Origin': '*'} )


async def get_user(request):

    uid = request.match_info['uid']

    userTuple = users.getOne(uid)

    user = {
        'id_pessoa': userTuple[0],
        'nome': userTuple[1],
        'data_admissao': userTuple[2].isoformat(),
    }
    print(user)

    return web.Response(text=json.dumps(user), headers={'Access-Control-Allow-Origin': '*'} )


async def add_user(request):
    try:
        body = await request.post()
        nome            = body["nome"]
        rg              = body["rg"]
        cpf             = body["cpf"]
        data_nascimento = body["data_nascimento"]
        data_admissao   = body["data_admissao"]
    except:
        res = {"error": "Corpo do request incompleto!"}
        return web.Response(text=json.dumps(res), headers={'Access-Control-Allow-Origin': '*'} )

    print(body)

    if (not validateCPF(body["cpf"])):
        res = {"error": "CPF inválido!"}
        return web.Response(text=json.dumps(res), headers={'Access-Control-Allow-Origin': '*'} )
        

    cursor = users.add(body)
    userTuple = users.getOneBy("nome", body["nome"])
    user = {
        'id_pessoa': userTuple[0],
        'nome': userTuple[1],
        'data_admissao': userTuple[2].isoformat(),
    }

    res = {"pessoa": user}
    return web.Response(text=json.dumps(res), headers={'Access-Control-Allow-Origin': '*'} )


async def delete_user(request):
    try:
        uid = request.match_info['uid']

        if not uid.isnumeric():
            res = {"error": "ID de pessoa inválido!"}
            return web.Response(text=json.dumps(res), headers={'Access-Control-Allow-Origin': '*'} )
    except:
        res = {"error": "ID vazio!"}
        return web.Response(text=json.dumps(res), headers={'Access-Control-Allow-Origin': '*'} )

    users.remove(uid)

    res = { "message" : "Pessoa deletada!" }
    return web.Response(text=json.dumps(res), headers={'Access-Control-Allow-Origin': '*'} )
    



app = web.Application()

app.add_routes([web.get('/users', get_users),
                web.get('/user/{uid}', get_user),
                web.get('/user/delete/{uid}', delete_user),
                web.post('/user/add', add_user),
                ])

web.run_app(app)


