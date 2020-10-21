from flask import Flask, request
from flasgger import Swagger
from nameko.standalone.rpc import ClusterRpcProxy

from services.Billboard import Billboard


# API configurations
app = Flask(__name__)
Swagger(app)
CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost"}


# API functions
@app.route('/attach', methods=['POST'])
def attach():
    """
    Attach a topic of interest onto the Exchange Billboard. It will be \
        collected and processed by a worker
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: data
          properties:
            want:
              type: string
            have:
              type: string
            league:
              type: string
    responses:
      200:
        description: Successfully attached topic
      400:
        description: Unable to create topic
    """
    want = request.json.get('want')
    have = request.json.get('have')
    league = request.json.get('league')
    with ClusterRpcProxy(CONFIG) as rpc:
        status_code, response = rpc.exchange_billboard.\
                                attach_topic(want, have, league)
        return response, status_code


@app.route('/detach', methods=['POST'])
def detach():
    """
    Detach a topic of interest from the Billboard, based on its index. The \
      "/topics" method can be called to display all topics and indexes
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: data
          properties:
            index:
              type: integer
    responses:
      200:
        description: Successfully detached topic from billboard
      400:
        description: Could not proccess this request, probably because the \
          given index is not an integer or its out of range
    """
    try:
        index = request.json.get('index')
        index = int(index)
    except ValueError as e:
        return 'Unable to cast "index: %s" as integer' % index, 400
    else:
        with ClusterRpcProxy(CONFIG) as rpc:
            status_code, response = rpc.exchange_billboard.detach_topic(index)
            return response, status_code


@app.route('/topics', methods=['GET'])
def display_available_topics():
    """
    Display all topics currently attached onto the Exchange Billboard.
    ---
    responses:
      200:
        description: Index, Want, Have of each topic
    """
    with ClusterRpcProxy(CONFIG) as rpc:
        status_code, response = rpc.exchange_billboard.\
                                display_available_topics()
        return response, status_code


@app.route('/topics/<index>', methods=['GET'])
def display_topic_info(index):
    """
    Display specific JSON information about a specific topic
    ---
    parameters:
      - name: index
        in: path
        required: true
        schema:
          type: integer
        description: The topic index
    responses:
      200:
        description: JSON payload of a given topic
    """
    try:
        topic_index = int(index)
    except ValueError:
        return 'Unable to cast topic index %s as integer' % index
    else:
        with ClusterRpcProxy(CONFIG) as rpc:
            status_code, response = rpc.exchange_billboard.\
                                    display_topic_info(topic_index)
            return response, status_code


app.run(debug=True)
