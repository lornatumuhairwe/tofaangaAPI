from flask import request, jsonify, Blueprint, abort, session, make_response
from my_app import db, app
from my_app.product.models import User, Bucketlist, BucketlistItem

bucketlistitems = Blueprint('bucketlistitems', __name__)


@bucketlistitems.route('/bucketlists/<int:bucketlistID>/items/', methods=['POST'])
def add_item_to_bucketlist(bucketlistID):
    if request.method=='POST':
        title = request.form.get('title')
        deadline = request.form.get('deadline')
        status = request.form.get('status')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter(Bucketlist.owner_id==resp).filter_by(id=bucketlistID).first()
                if bucketlist:
                    bucketlist_item = BucketlistItem(title, deadline,status)
                    db.session.add(bucketlist_item) # FK relationship
                    bucketlist.items.append(bucketlist_item)
                    db.session.commit()
                    res = {
                        'message': 'Bucketlist item added successfully',
                        'buckelist Item': bucketlist_item.title
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

@bucketlistitems.route('/bucketlists/<int:bucketlistID>/items/<int:BLitemID>', methods=['PUT','DELETE'])
def update_or_delete_item_in_bucketlist(bucketlistID, BLitemID):
    if request.method=='PUT':
        title = request.form.get('title')
        deadline = request.form.get('deadline')
        status = request.form.get('status')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist_item = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).filter_by(id=BLitemID).first()
                # bucketlist = Bucketlist.query.filter(Bucketlist.owner_id == resp).filter_by(id=bucketlistID).first()
                if bucketlist_item:
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
                else:
                    res = {
                        'message': 'Bucketlist item doesnt exist'
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
                bucketlist_item = BucketlistItem.query.filter(BucketlistItem.bucketlist_id == bucketlistID).filter_by(
                    id=BLitemID).first()
                if bucketlist_item:
                    db.session.delete(bucketlist_item)
                    db.session.commit()
                    res = {
                        'message': 'Bucketlist item deleted successfully'
                    }
                else:
                    res = {
                        'message': 'Bucketlist item doesnt exist'
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