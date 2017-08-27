from flask import request, jsonify, Blueprint
from my_app import db
from my_app.product.models import User, Bucketlist, BucketlistItem
from my_app.decorators import authenticate

bucketlist = Blueprint('bucketlist', __name__, url_prefix='/api/v1/bucketlists/')


@bucketlist.route('', methods=['POST'])
@authenticate
def add_bucketlist(user_id):
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
                201:
                  description: "Bucketlist Added Successfully"
                400:
                  description: "Bucketlist Add Failed. Bad request, use appropriate parameters"
                401:
                  description: "Bucketlist Add Failed. Invalid token, Login again or Token not found, Login to get one"
           """
    name = request.form.get('name')
    if not name:
        res = {
            'message': 'Bucketlist item should have name'
        }
        return jsonify(res), 400
    user = User.query.filter_by(id=user_id).first()
    item = Bucketlist.query.filter(Bucketlist.owner_id == user_id).filter_by(name=name).first()
    if not item:
        bucketlist = Bucketlist(name=name)
        db.session.add(bucketlist)
        user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        res = {
            'bucketlist': bucketlist.name,
            'message': 'Bucketlist added successfully'
        }
        return jsonify(res), 201
    else:
        res = {
            'message': 'Bucketlist exists'
        }
        return jsonify(res), 400


@bucketlist.route('', methods=['GET'])
@authenticate
def view_bucketlist(user_id):
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

    search_name = request.args.get('q', '')  # http://localhost:5000/bucketlists/?q=Oceania, implements this kind
    #  of search
    limit = request.args.get('limit', '')
    if limit and search_name:
        result = Bucketlist.query.filter(Bucketlist.name.ilike('%' + search_name + '%')). \
            filter_by(owner_id=user_id).paginate(page=1, per_page=int(limit)).items
        if len(result) > 0:
            res = {
                bucketlist.id: bucketlist.name for bucketlist in result
            }
            return jsonify(res), 200
        else:
            res = {
                'message': 'No result matches this search'
            }
            return jsonify(res), 200

    elif limit:
        limit_result = Bucketlist.query.filter_by(owner_id=user_id).paginate(page=1, per_page=int(limit)).items
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

    elif search_name:
        search_result = Bucketlist.query.filter(Bucketlist.name.ilike('%' + search_name + '%')). \
            filter_by(owner_id=user_id).all()
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
        if len(Bucketlist.query.filter_by(owner_id=user_id).all()) > 0:
            res = {
                bucketlist.id: bucketlist.name for bucketlist in Bucketlist.query.filter_by(owner_id=user_id).all()
            }
            return jsonify(res), 200
        else:
            res = {
                'message': 'No bucketlists yet.'
            }
            return jsonify(res), 200


@bucketlist.route('<int:bucketlistID>', methods=['PUT'])
@authenticate
def update_bucketlist(user_id, bucketlistID):
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
                201:
                  description: "Bucketlist updated Successfully"
                400:
                  description: "Bucketlist update Failed. Bad request, use appropriate parameters"
                401:
                  description: "Bucketlist update Failed. Invalid token, Login again or Token not found, Login to get one"
           """
        #res = {'message': 'Update Function!'}
    newname = request.form.get('newname')
    auth_token = request.headers.get('Authorization')
    bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == user_id).filter_by(id=bucketlistID).first()
    if bucketlist:
        bucketlist.name = newname
        db.session.commit()
        res = {
            #bucketlist.id: bucketlist.name,
            'message': 'Bucketlist updated successfully'
        }
        return jsonify(res), 201
    else:
        res = {
            'message': 'Bucketlist doesnt exist'
        }
        return jsonify(res), 400


@bucketlist.route('<int:bucketlistID>', methods=['GET'])
@authenticate
def view_one_bucketlist(user_id, bucketlistID):
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
    # name = request.form.get('name')
    auth_token = request.headers.get('Authorization')
    search_name = request.args.get('q', '')  # http://localhost:5000/bucketlists/1?q=Oceania
    limit = request.args.get('limit', '')
    if limit and search_name:
        bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == user_id).filter_by(id=bucketlistID).first()
        if bucketlist:
            result =  BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).\
                filter(BucketlistItem.title.ilike('%'+search_name+'%')).paginate(page=1, per_page=int(limit)).\
                items
            if len(result) > 0:
                res = {
                    bucketlistItem.id: bucketlistItem.title for bucketlistItem in result
                }
                return jsonify(res), 200
            else:
                res = {
                    'message': 'No result matches this search'
                }
                return jsonify(res), 200
    elif limit:
        bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == user_id).filter_by(id=bucketlistID).first()
        if bucketlist:
            limit_result = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).\
                paginate(page=1, per_page=int(limit)).items
            if len(limit_result) > 0:
                res = {
                    bucketlistItem.id: bucketlistItem.title for bucketlistItem in limit_result
                }
                return jsonify(res), 200
            else:
                res = {
                    'message': 'No items in this bucketlist'
                }
                return jsonify(res), 200
        else:
            res = {
                'message': "Bucketlist doesn't exist"
            }
            return jsonify(res), 200
    elif search_name:
        # search_result = Bucketlist.query.filter(Bucketlist.name.match('%'+search_name+'%')).\
        #     filter_by(owner_id=resp).all()
        bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == user_id).filter_by(id=bucketlistID).first()
        if bucketlist:
            search_result = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).\
                filter(BucketlistItem.title.ilike('%'+search_name+'%'))
            if search_result.count() > 0: # lenngth of a base query
                res = {
                    bucketlistItem.id: bucketlistItem.title for bucketlistItem in search_result
                    }
                return jsonify(res), 200
            else:
                res = {
                    'message': 'Bucketlist not found'
                }
                return jsonify(res), 200
        else:
            res = {
                'message': 'Bucketlist doesnt exist'
            }
            return jsonify(res), 400
    else:
        bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == user_id).filter_by(id=bucketlistID).first()
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


@bucketlist.route('<int:bucketlistID>', methods=['DELETE'])
@authenticate
def delete_bucketlist(user_id, bucketlistID):
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
    bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == user_id).filter_by(id=bucketlistID).first()
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
