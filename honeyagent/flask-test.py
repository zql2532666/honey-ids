import yaml, json
# from DbAccess import *
from gevent.pywsgi import WSGIServer
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, jsonify, abort

# TODO:
# //add in gevent
# //db connections


app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

# Configure DB
# db = yaml.load(open('db.yaml'), Loader=yaml.SafeLoader)
# app.config['MYSQL_HOST'] = db['mysql_host']
# app.config['MYSQL_USER'] = db['mysql_user']
# app.config['MYSQL_PASSWORD'] = db['mysql_password']
# app.config['MYSQL_DB'] = db['mysql_db']

# mysql = MySQL(app)

# For testing purposes with jinja. Remove later
# Usage: {{ mdebug("whatever to print here") }}
@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Dashboard V1")

@app.route("/index2")
def index2():
    return render_template("index2.html", title="Dashboard V2")

@app.route("/index3")
def index3():
    return render_template("index3.html", title="Dashboard V3")

@app.route("/deploy", methods=['GET', 'POST'])
def deploy():
    return render_template("deploy.html", title="Honeypot Deployment")

@app.route("/nodes")
def nodes():
    return render_template("nodes.html", title="Nodes")

# Uncomment for testing
# @app.route("/test", methods=['GET', 'POST'])
# def test():
#     return render_template("test.html")

# CRUD endpoints
# Retrieve all honeynodes
@app.route("/api/v1/honeynodes/", methods=['GET'])
def retrieveAllNodes():
    print("yay you are getting all the nodes")
    json_data = {}

    #Mysql connection
    cur = mysql.connection.cursor()

    sql = "select * from nodes"
    resultValue = cur.execute(sql)
    if resultValue > 0:
        my_query = DbAccess.query_db(cur)
        json_data = json.dumps(my_query, default=DbAccess.myconverter)

    return str(json_data)

#Retrieve single honeynode
@app.route("/api/v1/honeynodes/<string:token>", methods=['GET'])
def retrieveNode(token):

    json_data = {}

    #Mysql connection
    cur = mysql.connection.cursor()

    sql = f"select * from nodes where token={token}"
    resultValue = cur.execute(sql)
    if resultValue > 0:
        my_query = DbAccess.query_db(cur)
        json_data = json.dumps(my_query, default=DbAccess.myconverter)

    return str(json_data)

# Create honeynode
# Change accordingly with derek's data
# Current data format to insert
# {
#        "honeynode_name" : "test",
#        "ip_addr" : "192.168.1.2",
#        "subnet_mask" : "255.255.255.0",
#        "honeypot_type" : "test",
#        "nids_type" : "null",
#        "no_of_attacks" : "2",
#        "date_deployed" : "2020-01-01 10:10:10",
#        "heartbeat_status" : "down",
#        "last_heard" : "idk",
#        "token" : "2"
# }
@app.route("/api/v1/honeynodes/", methods=['POST'])
def createNode():

    if not request.json or not 'token' in request.json:
        abort(400)

    #Mysql connection
    cur = mysql.connection.cursor()

    honeynode_name = request.json['honeynode_name']
    ip_addr = request.json['ip_addr']
    subnet_mask = request.json['subnet_mask']
    honeypot_type = request.json['honeypot_type']
    nids_type = request.json['nids_type']
    no_of_attacks = request.json['no_of_attacks']
    date_deployed = request.json['date_deployed']
    heartbeat_status = request.json['heartbeat_status']
    last_heard = request.json['last_heard']
    token = request.json['token']

    sql = f"insert into nodes(honeynode_name, ip_addr, subnet_mask, honeypot_type, nids_type, no_of_attacks, date_deployed, heartbeat_status, token, last_heard) \
        values('%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', '%s')" % (honeynode_name, ip_addr, subnet_mask, honeypot_type, nids_type, int(no_of_attacks), date_deployed, heartbeat_status, token, last_heard)
    
    resultValue = 0

    try:
        resultValue = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    if resultValue == 0:
        abort(404)

    return jsonify({'success': True}), 201

# Update honeynode
@app.route("/api/v1/honeynodes/<string:token>", methods=['PUT'])
def updateNode(token):
    
    if not request.json or not token:
        abort(400)

    #Mysql connection
    cur = mysql.connection.cursor()

    honeynode_name = '' if not request.json.__contains__('honeynode_name') else request.json['honeynode_name']
    ip_addr = '' if not request.json.__contains__('ip_addr') else request.json['ip_addr']
    subnet_mask = '' if not request.json.__contains__('subnet_mask') else request.json['subnet_mask']
    honeypot_type = '' if not request.json.__contains__('honeypot_type') else request.json['honeypot_type']
    nids_type = '' if not request.json.__contains__('nids_type') else request.json['nids_type']
    no_of_attacks = '' if not request.json.__contains__('no_of_attacks') else int(request.json['no_of_attacks'])
    date_deployed = '' if not request.json.__contains__('date_deployed') else request.json['date_deployed']
    heartbeat_status = '' if not request.json.__contains__('heartbeat_status') else request.json['heartbeat_status']
    last_heard = '' if not request.json.__contains__('last_heard') else request.json['last_heard']

    sql = f"update nodes set honeynode_name=IF('{honeynode_name}' = '', honeynode_name, '{honeynode_name}'), \
        ip_addr=IF('{ip_addr}' = '', ip_addr, '{ip_addr}'), \
        subnet_mask=IF('{subnet_mask}' = '', subnet_mask, '{subnet_mask}'), \
        honeypot_type=IF('{honeypot_type}' = '', honeypot_type, '{honeypot_type}'), \
        nids_type=IF('{nids_type}' = '', nids_type, '{nids_type}'), \
        no_of_attacks=IF('{no_of_attacks}' = '', no_of_attacks, '{no_of_attacks}'), \
        date_deployed=IF('{date_deployed}' = '', date_deployed, '{date_deployed}'), \
        heartbeat_status=IF('{heartbeat_status}' = '', heartbeat_status, '{heartbeat_status}'), \
        last_heard=IF('{last_heard}' = '', last_heard, '{last_heard}') where token='{token}'"
    
    resultValue = 0

    try:
        resultValue = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    if resultValue == 0:
        abort(404, "no values inserted")

    return jsonify({'success': True}), 200


# Delete honeynode
@app.route("/api/v1/honeynodes/<string:token>", methods=['DELETE'])
def deleteNode(token):

    if not token:
        abort(400)

    #Mysql connection
    cur = mysql.connection.cursor()

    sql = f"delete from nodes where token='{token}'"
    
    resultValue = 0

    try:
        resultValue = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    if resultValue == 0:
        abort(404)

    return jsonify({'success': True}), 200

if __name__ == "__main__":
    try:
        http_server = WSGIServer(('0.0.0.0', 5000), app)
        app.debug = True
        print('Waiting for requests.. ')
        http_server.serve_forever()
    except:
        print("Exception")
    # app.run(host="0.0.0.0", debug = True)

