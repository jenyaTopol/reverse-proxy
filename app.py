from flask import Flask, request
import mysql.connector
import requests

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'your_mysql_host'
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'your_mysql_database'

# Connect to MySQL
def connect_to_mysql():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

# Toggle the reverse proxy status
@app.route('/proxy/toggle', methods=['POST'])
def toggle_proxy():
    status = request.json.get('status')
    
    # Update the status in the database
    connection = connect_to_mysql()
    cursor = connection.cursor()
    cursor.execute("UPDATE proxy_config SET enabled = %s", (status,))
    connection.commit()
    cursor.close()
    connection.close()
    
    return {'message': 'Proxy toggled successfully'}

# Reverse proxy logic
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def reverse_proxy(path):
    # Fetch the routing rule from the database based on the path
    connection = connect_to_mysql()
    cursor = connection.cursor()
    cursor.execute("SELECT target_url FROM routing_rules WHERE path = %s", (path,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if result:
        target_url = result[0]
        method = request.method
        headers = request.headers
        data = request.get_data()
        
        # Make a request to the target URL
        response = requests.request(method, target_url, headers=headers, data=data)
        
        # Create a Flask response with the received response data
        flask_response = app.response_class(
            response=response.content,
            status=response.status_code,
            headers=response.headers.items()
        )
        
        return flask_response
    else:
        return {'message': 'No routing rule found for the path'}

if __name__ == '__main__':
    app.run()
