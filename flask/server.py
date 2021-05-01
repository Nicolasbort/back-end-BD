from flask import Flask, render_template, redirect, request
from flask_mysqldb import MySQL
from modules.Database import * 
import re

app = Flask(__name__)

app.config['MYSQL_HOST']     = 'jobs.visie.com.br'
app.config['MYSQL_USER']     = 'nicolasbortoluzzi'
app.config['MYSQL_PASSWORD'] = 'bmljb2xhc2Jv'
app.config['MYSQL_DB']       = 'nicolasbortoluzzi'


mysql = MySQL(app)

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
        query = 'SELECT id_pessoa, nome, data_admissao FROM {}'.format(self.table_name)
        return db.setQuery(query).execute().fetchall()

    def getOne(self, uid):
        query = 'SELECT id_pessoa, nome, data_admissao FROM {} WHERE id_pessoa = {}'.format(self.table_name, uid)
        return db.setQuery(query).execute().fetchone()

    def getOneBy(self, key, value):
        query = "SELECT id_pessoa, nome, data_admissao FROM {} WHERE {} = '{}'".format(self.table_name, key, value)
        return db.setQuery(query).execute().fetchone()




@app.route("/user/add", methods=['POST'])
def add_user():
    data = request.form.to_dict(flat=True)

    try:
        nome            = data["nome"]
        rg              = data["rg"]
        cpf             = data["cpf"]
        data_nascimento = data["data_nascimento"]
        data_admissao   = data["data_admissao"]
    except:
        return redirect('/')

    if (validateCPF(cpf)):
        query = "INSERT INTO pessoas (`nome`,`rg`, `cpf`,`data_nascimento`, `data_admissao`) VALUES ('{}', '{}','{}', '{}','{}')".format(nome, rg, cpf, data_nascimento, data_admissao)
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close()

        return redirect('/')

    print(cpf + " invalido")
    return redirect('/')



@app.route("/user/delete", methods=['POST'])
def delete_user():

    data = request.form.to_dict(flat=True)
    try:
        uid = data["id_pessoa"]
    except:
        return redirect("/", code=400)


    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM pessoas WHERE id_pessoa = {}".format(uid))
    mysql.connection.commit()
    cursor.close()

    return redirect("/")


@app.route("/")
def home():
    # data = usrs.getAll()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_pessoa, nome, data_admissao FROM pessoas")
    data = cursor.fetchall()
    cursor.close()
    return render_template("home.html", pessoas=data)


if __name__ == '__main__':
    app.run()
