from flask import request, jsonify, Blueprint, abort, session, make_response
from my_app import db, app
from my_app.product.models import User, Bucketlist, BucketlistItem

bucketlist = Blueprint('bucketlist', __name__)

@bucketlist.route('/bucketlists/', methods=['POST', 'GET'])
def add_or_view_bucketlist():
    """ Adding a bucketlist
                ---
                tags:
                  - "Bucketlist operations"
                parameters:
                  - in: "body"
                    name: "Add Buckelist"
                    description: "User adds a bucketlist, the operation requires a user to be logged in"
                    required: false
                    schema:
                      type: "object"
                      required:
                      - "name"
                      properties:
                        name:
                          type: "string"
                responses:
                    200:
                      description: "Bucketlist added successfully"
                    400:
                      description: "Bucketlist addition Failed"
                    401:
                      description: "PLease Login to use the application"
               """
    if request.method=='POST':
        name = request.form.get('name')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                user = User.query.filter_by(id=resp).first()
                item = Bucketlist.query.filter(Bucketlist.owner_id==resp).filter_by(name=name).first()
                #item = Bucketlist.query.filter_by(name=name).first()
                if not item:
                    bucketlist = Bucketlist(name=name)
                    db.session.add(bucketlist)
                    user.bucketlists.append(bucketlist) # FK relationship
                    db.session.commit()
                    res = {
                        'bucketlist': bucketlist.name
                    }
                else:
                    res = {
                        'message': 'Bucketlist exists'
                    }
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
        return jsonify(res)

    """ Viewing all bucketlists
                ---
                tags:
                  - "Bucketlist operations"
                parameters:
                  - in: "body"
                    name: "Add Buckelist"
                    description: "User views all his/her bucketlists, the operation requires a user to be logged in"
                    required: false
                    schema:
                      type: "object"
                responses:
                    200:
                      description: "Bucketlist locaded successfully"
                    400:
                      description: "Bucketlist loading Failed"
                    401:
                      description: "PLease Login to use the application"
               """
    if request.method == 'GET':
        search_name = request.args.get('q', '') #http://localhost:5000/bucketlists/?q=Oceania, implements this kind of search
        limit = request.args.get('limit', '')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int) and limit:
                limit_result = Bucketlist.query.filter_by(owner_id=resp).paginate(page=1, per_page=int(limit)).items
                res = {
                    bucketlist.id: bucketlist.name for bucketlist in limit_result
                }
            elif isinstance(resp, int) and not search_name:
                res = {
                    bucketlist.id: bucketlist.name for bucketlist in Bucketlist.query.filter_by(owner_id=resp).all()
                }
            elif isinstance(resp, int) and search_name:
                search_result = Bucketlist.query.filter(Bucketlist.name.match('%'+search_name+'%')).filter_by(owner_id=resp).all()
                if search_result:
                    res = {

                        bucketlist.id: bucketlist.name for bucketlist in search_result
                        }
                else:
                    res = {
                        'message': 'Bucketlist not found'
                    }
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
        return jsonify(res)

@bucketlist.route('/bucketlists/<int:bucketlistID>', methods=['PUT','DELETE', 'GET'])

def view_update_delete_bucketlist(bucketlistID):
    """ Updating a bucketlist
                            ---
                            tags:
                              - "Bucketlist operations"
                            parameters:
                              - in: "body"
                                name: "Updating Buckelist"
                                description: "User updates a bucketlist, the operation requires a user to be logged in"
                                required: false
                                schema:
                                  type: "object"
                                  required:
                                  - "newname"
                                  properties:
                                    newname:
                                      type: "string"
                            responses:
                                200:
                                  description: "Bucketlist updated successfully"
                                400:
                                  description: "Bucketlist update Failed"
                                401:
                                  description: "PLease Login to use the application"

                           """
    if request.method=='PUT':
        #res = {'message': 'Update Function!'}
        newname = request.form.get('newname')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == resp).filter_by(id=bucketlistID).first()
                if bucketlist:
                    bucketlist.name = newname
                    db.session.commit()
                    res = {
                        #bucketlist.id: bucketlist.name,
                        'message': 'Bucketlist updated successfully'
                    }
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
                    }
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
        return jsonify(res)

    if request.method == 'GET':
        # name = request.form.get('name')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == resp).filter_by(id=bucketlistID).first()
                if bucketlist:
                    res = {
                        bucketlist.id: bucketlist.name
                    }
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
                    }
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
        return jsonify(res)

    if request.method=='DELETE':
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == resp).filter_by(id=bucketlistID).first()
                if bucketlist:
                    db.session.delete(bucketlist)
                    db.session.commit()
                    res = {
                        'message': 'Bucketlist deleted successfully'
                    }
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
                    }
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
        return jsonify(res)
