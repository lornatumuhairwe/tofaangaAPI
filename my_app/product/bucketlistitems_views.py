from flask import request, jsonify, Blueprint
from my_app import db
from my_app.product.models import Bucketlist, BucketlistItem
from my_app.decorators import authenticate

bucketlistitems = Blueprint('bucketlistitems', __name__, url_prefix='/api/v1')


@bucketlistitems.route('/bucketlists/<int:bucketlistID>/items/', methods=['POST'])
@authenticate
def add_item_to_bucketlist(user_id, bucketlistID):
    """Add item to bucketlist
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
                - name: title
                  in: "formData"
                  description: "The title for the new item"
                  required: true
                  type: "string"
                - name: deadline
                  in: "formData"
                  description: "The deadline for the new item"
                  required: true
                  type: "string"
                - name: status
                  in: "formData"
                  description: "The status for the new item"
                  required: true
                  type: "string"
                responses:
                    201:
                      description: "Bucketlist item added Successfully"
                    400:
                      description: "Bucketlist item addition Failed. Bad request, use appropriate parameters"
                    401:
                      description: "Bucketlist item addition Failed.  Invalid token, Login again or Token not found, Login to get one"
               """
    title = request.form.get('title')
    deadline = request.form.get('deadline')
    status = request.form.get('status')
    if not title:
        res = {
            'message': 'Bucketlist item has to have a title. Try again.'
        }
        return jsonify(res), 400
    bucketlist = Bucketlist.query.filter(Bucketlist.owner_id==user_id).filter_by(id=bucketlistID).first()
    bucketlistItem = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID). \
        filter(BucketlistItem.title == title).first()
    #print (bucketlistItem)
    if bucketlist and not bucketlistItem:
        bucketlist_item = BucketlistItem(title, deadline,status)
        db.session.add(bucketlist_item)  # FK relationship
        bucketlist.items.append(bucketlist_item)
        db.session.commit()
        res = {
            'message': 'Bucketlist item added successfully',
            'buckelist Item': bucketlist_item.title
        }
        return jsonify(res), 201
    elif bucketlistItem:
        res = {
            'message': "Bucketlist item with name exists"
        }
        return jsonify(res), 400
    else:
        res = {
            'message': "Bucketlist doesn't exist"
        }
        return jsonify(res), 400


@bucketlistitems.route('/bucketlists/<int:bucketlistID>/items/<int:BLitemID>', methods=['PUT'])
@authenticate
def update_item_in_bucketlist(user_id, bucketlistID, BLitemID):
    """Update item in bucketlist
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
                - name: BLitemID
                  in: "path"
                  description: "The ID the bucketlist"
                  required: true
                  type: "string"
                - name: title
                  in: "formData"
                  description: "The title for the new item"
                  required: true
                  type: "string"
                - name: deadline
                  in: "formData"
                  description: "The deadline for the new item"
                  required: true
                  type: "string"
                - name: status
                  in: "formData"
                  description: "The status for the new item"
                  required: true
                  type: "string"
                responses:
                    201:
                      description: "Bucketlist item updated Successfully"
                    400:
                      description: "Bucketlist item update Failed. Bad request, use appropriate parameters"
                    401:
                      description: "Bucketlist item update Failed. Invalid token, Login again or Token not found, Login to get one"
        """
    title = request.form.get('title')
    deadline = request.form.get('deadline')
    status = request.form.get('status')
    bucketlist_item = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).\
        filter_by(id=BLitemID).first()
    bucketlistItem = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID). \
        filter(BucketlistItem.title == title).first()
    if not title:
        res = {
            'message': 'Bucketlist item has to have a title. Try again.'
        }
        return jsonify(res), 400
    # bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == resp).filter_by(id=bucketlistID).first()
    elif bucketlist_item and not bucketlistItem:
        bucketlist_item.title = title
        bucketlist_item.deadline = deadline
        bucketlist_item.status = status
        db.session.commit()
        res = {
            'buckelist Item': bucketlist_item.title,
            'Deadline': bucketlist_item.deadline,
            'status': bucketlist_item.status,
            'message': 'Bucketlist item updated successfully'
        }
        return jsonify(res), 201
    elif bucketlistItem:
        res = {
            'message': "Bucketlist item with name exists"
        }
        return jsonify(res), 400
    else:
        res = {
            'message': 'Bucketlist item doesnt exist'
        }
        return jsonify(res), 400


@bucketlistitems.route('/bucketlists/<int:bucketlistID>/items/<int:BLitemID>', methods=['DELETE'])
@authenticate
def delete_item_in_bucketlist(user_id, bucketlistID, BLitemID):
    """Delete item in bucketlist
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
                - name: BLitemID
                  in: "path"
                  description: "The ID the bucketlist"
                  required: true
                  type: "string"
                responses:
                    200:
                      description: "Bucketlist item delete Successfully"
                    400:
                      description: "Bucketlist item delete Failed. Bad request, use appropriate parameters"
                    401:
                      description: "Bucketlist item delete Failed. Invalid token, Login again or Token not found, Login to get one"
        """
    bucketlist_item = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).filter_by(
        id=BLitemID).first()
    if bucketlist_item:
        db.session.delete(bucketlist_item)
        db.session.commit()
        res = {
            'message': 'Bucketlist item deleted successfully'
        }
        return jsonify(res), 200
    else:
        res = {
            'message': "Bucketlist item doesn't exist"
        }
        return jsonify(res), 400
