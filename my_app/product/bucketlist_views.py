from flask import request, jsonify, Blueprint
from my_app import db
from my_app.product.models import User, Bucketlist, BucketlistItem

bucketlist = Blueprint('bucketlist', __name__)


@bucketlist.route('/bucketlists/', methods=['POST'])
def add_bucketlist():
    """ Adding a bucketlist
            ---
            tags:
            - "Bucketlist operations"
            consumes:
                - "multipart/form-data"
            produces:
                - "application/json"
            parameters:
            - name: "Authorization"
              in: "header"
              description: "Token of a logged in user"
              required: true
              type: "string"
            - name: "name"
              in: "formData"
              description: "Token of a logged in user"
              required: true
              type: "string"
            responses:
                200:
                  description: "Bucketlist Added Successfully"
                400:
                  description: "Bucketlist Add Failed. Bad request, use appropriate parameters"
                401:
                  description: "Bucketlist Add Failed. Invalid token, Login again or Token not found, Login to get one"
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
                    user.bucketlists.append(bucketlist)  # FK relationship
                    db.session.commit()
                    res = {
                        'bucketlist': bucketlist.name,
                        'message': 'Bucketlist added successfully'
                    }
                    return jsonify(res), 200
                else:
                    res = {
                        'message': 'Bucketlist exists'
                    }
                    return jsonify(res), 400
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
                return jsonify(res), 401
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
            return jsonify(res), 401


@bucketlist.route('/bucketlists/', methods=['GET'])
def view_bucketlist():
    """ View bucketlists
            ---
            tags:
            - "Bucketlist operations"
            consumes:
                - "multipart/form-data"
            produces:
                - "application/json"
            parameters:
            - name: "Authorization"
              in: "header"
              description: "Token of a logged in user"
              required: true
              type: "string"
            - name: q
              in: "query"
              description: "Bucketlist a user would like to search for"
              required: false
              type: "string"
            - name: limit
              in: "query"
              description: "The maximum number of bucketlists that a user would like to return"
              required: false
              type: "integer"
            responses:
                200:
                  description: "Bucketlist retrieved Successfully"
                400:
                  description: "Bucketlist retrieval Failed. Bad request, use appropriate parameters"
                401:
                  description: "Bucketlist retrieval Failed. Invalid token, Login again or Token not found, Login to get one"
           """
    if request.method == 'GET':
        search_name = request.args.get('q', '')  # http://localhost:5000/bucketlists/?q=Oceania, implements this kind
        #  of search
        limit = request.args.get('limit', '')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int) and limit:
                limit_result = Bucketlist.query.filter_by(owner_id=resp).paginate(page=1, per_page=int(limit)).items
                if len(limit_result) > 0:
                    res = {
                        bucketlist.id: bucketlist.name for bucketlist in limit_result
                    }
                    return jsonify(res), 200
                else:
                    res = {
                        'message': 'No bucketlists yet.'
                        }
                    return jsonify(res), 200
            elif isinstance(resp, int) and not search_name:
                if len(Bucketlist.query.filter_by(owner_id=resp).all()) > 0:
                    res = {
                        bucketlist.id: bucketlist.name for bucketlist in Bucketlist.query.filter_by(owner_id=resp).all()
                    }
                    return jsonify(res), 200
                else:
                    res = {
                        'message': 'No bucketlists yet.'
                    }
                    return jsonify(res), 200
            elif isinstance(resp, int) and search_name:
                search_result = Bucketlist.query.filter(Bucketlist.name.match('%'+search_name+'%')).\
                    filter_by(owner_id=resp).all()
                if search_result:
                    res = {
                        bucketlist.id: bucketlist.name for bucketlist in search_result
                        }
                    return jsonify(res), 200
                else:
                    res = {
                        'message': 'Bucketlist not found'
                    }
                    return jsonify(res), 200
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
                return jsonify(res), 401
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
            return jsonify(res), 401


@bucketlist.route('/bucketlists/<int:bucketlistID>', methods=['PUT'])
def update_bucketlist(bucketlistID):
    """ Update bucketlist
            ---
            tags:
            - "Bucketlist operations"
            consumes:
                - "multipart/form-data"
            produces:
                - "application/json"
            parameters:
            - name: "Authorization"
              in: "header"
              description: "Token of a logged in user"
              required: true
              type: "string"
            - name: bucketlistID
              in: "path"
              description: "The ID the bucketlist"
              required: true
              type: "string"
            - name: newname
              in: "formData"
              description: "The new name of the bucketlist"
              required: true
              type: "string"
            responses:
                200:
                  description: "Bucketlist updated Successfully"
                400:
                  description: "Bucketlist update Failed. Bad request, use appropriate parameters"
                401:
                  description: "Bucketlist update Failed. Invalid token, Login again or Token not found, Login to get one"
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
                    return jsonify(res), 200
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
                    }
                    return jsonify(res), 400
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
                return jsonify(res), 401
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
            return jsonify(res), 401


@bucketlist.route('/bucketlists/<int:bucketlistID>', methods=['GET'])
def view_one_bucketlist(bucketlistID):
    """ View bucketlist
            ---
            tags:
            - "Bucketlist operations"
            consumes:
                - "multipart/form-data"
            produces:
                - "application/json"
            parameters:
            - name: "Authorization"
              in: "header"
              description: "Token of a logged in user"
              required: true
              type: "string"
            - name: bucketlistID
              in: "path"
              description: "The ID the bucketlist"
              required: true
              type: "string"
            responses:
                200:
                  description: "Successful"
                400:
                  description: "Get Items in Bucketlist failed. Bad request, use appropriate parameters"
                401:
                  description: "Get Items in Bucketlist failed. Invalid token, Login again or Token not found, Login to get one"
               """
    if request.method == 'GET':
        # name = request.form.get('name')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == resp).filter_by(id=bucketlistID).first()
                bucketlistItems = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).all()
                if bucketlist:
                    if len(bucketlistItems)>0:
                        res = {
                            bucketlistItem.id: bucketlistItem.title for bucketlistItem in bucketlistItems
                        }
                        return jsonify(res), 200
                    else:
                        res = {
                            'message': 'No items in this bucketlist'
                        }
                        return jsonify(res), 200
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
                    }
                    return jsonify(res), 400
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
                return jsonify(res), 401
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
            return jsonify(res), 401

@bucketlist.route('/bucketlists/<int:bucketlistID>', methods=['DELETE'])
def delete_bucketlist(bucketlistID):
    """ Delete bucketlist
            ---
            tags:
            - "Bucketlist operations"
            consumes:
                - "multipart/form-data"
            produces:
                - "application/json"
            parameters:
            - name: "Authorization"
              in: "header"
              description: "Token of a logged in user"
              required: true
              type: "string"
            - name: bucketlistID
              in: "path"
              description: "The ID the bucketlist"
              required: true
              type: "string"
            responses:
                200:
                  description: "Delete Successful"
                400:
                  description: "Delete Failed. Bad request, use appropriate parameters"
                401:
                  description: "Delete Failed. Invalid token, Login again or Token not found, Login to get one"
           """
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
                    return jsonify(res), 200
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
                    }
                    return jsonify(res), 400
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
                return jsonify(res), 401
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
            return jsonify(res), 401
