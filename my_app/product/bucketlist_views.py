from flask import request, jsonify, Blueprint, url_for
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
@bucketlist.route('page/<int:page>', methods=['GET'])
@authenticate
def view_bucketlist(user_id, page=1):
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
            - name: page
              in: "query"
              description: "The page number the user wants to view"
              required: false
              type: "string"
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
    limit = request.args.get('limit', 4)
    # page = request.args.get('page', 1)

    if limit and search_name:
        result = Bucketlist.query.filter(Bucketlist.name.ilike('%' + search_name + '%')). \
            filter_by(owner_id=user_id).paginate(page, per_page=int(limit))
        result_list = result.items
        if len(result_list) > 0:
            pages = {'page': page, 'per_page': result.per_page, 'total': result.total, 'pages': result.pages}
            if result.has_prev:
                pages['prev_url'] = url_for(request.endpoint, page=result.prev_num, limit=int(limit))
            # else:
            #     pages['prev_url'] = None
            if result.has_next:
                pages['next_url'] =  url_for( request.endpoint, page=result.next_num, limit=int(limit), q=search_name)
            # else:
            #     pages['next_url'] = None
            # pages['first_url'] = url_for(request.endpoint, page=1,
            #                              per_page=per_page, expanded=expanded,
            #                              _external=True, **kwargs)
            # pages['last_url'] = url_for(request.endpoint, page=p.pages,
            #                             per_page=per_page, expanded=expanded,
            #                             _external=True, **kwargs)
            res = {
                'bucketlists': {bucketlist.id: bucketlist.name for bucketlist in result_list},
                'details': pages
                # 'results': limit_result.__dict__
            }
            return jsonify(res), 200
        else:
            res = {
                'message': 'Bucketlist not found'
            }
            return jsonify(res), 200

    elif limit:
        limit_result = Bucketlist.query.filter_by(owner_id=user_id).order_by(Bucketlist.id.desc()).paginate(page, per_page=int(limit))
        result_list = limit_result.items
        # if page > 1:
        #     limit_result = Bucketlist.query.filter_by(owner_id=user_id).limit(limit).offset((page-1)*limit)
        # else:
        #     limit_result = Bucketlist.query.filter_by(owner_id=user_id).paginate(page, per_page=int(limit)).items
        if len(limit_result.items) > 0:
            pages = {'page': page, 'per_page': limit_result.per_page, 'total': limit_result.total, 'pages': limit_result.pages}
            if limit_result.has_prev:
                pages['prev_url'] = url_for(request.endpoint, page=limit_result.prev_num, limit=int(limit))
            # else:
            #     pages['prev_url'] = None
            if limit_result.has_next:
                pages['next_url'] =  url_for( request.endpoint, page=limit_result.next_num, limit=int(limit))
            # else:
            #     pages['next_url'] = None
            # pages['first_url'] = url_for(request.endpoint, page=1,
            #                              per_page=per_page, expanded=expanded,
            #                              _external=True, **kwargs)
            # pages['last_url'] = url_for(request.endpoint, page=p.pages,
            #                             per_page=per_page, expanded=expanded,
            #                             _external=True, **kwargs)
            res = {
                'bucketlists': {bucketlist.id: bucketlist.name for bucketlist in result_list},
                'details': pages
                # 'results': limit_result.__dict__
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
