from flask import Blueprint, request, jsonify
from app.models import Reservations, Resource, db
from app.services.auth_service import token_required, permission_collector
from datetime import datetime

reservations_blueprint = Blueprint("reservations", __name__)

@reservations_blueprint.route("/reservations", methods=["GET"])
@token_required
def get_resvations(current_user):
    reservations = Reservations.query.filter_by(user_id=current_user.id).all()
    output = []
    for reservation in reservations:
        reservation_data = {
            'id': reservation.id,
            'resource_id': reservation.resource_id,
            'resource_name': reservation.resource.name,
            'start_time': reservation.start_time.isoformat(),
            'end_time': reservation.end_time.isoformat()
        }
        output.append(reservation_data)
    return jsonify({"reservations":output}), 200


@reservations_blueprint.route("/reservations", methods=["POST"])
@token_required
@permission_collector
def create_reservation(current_user, user_permissions):
    data = request.get_json()
    resource_id = data["resource_id"]
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time'])

    resource = Resource.query.get_or_404(resource_id)
    resource_permissions = set([perm.name for perm in resource.permissions])
    if not (resource_permissions & user_permissions):
        return jsonify({'message': 'Permission denied!'}), 403
    
    if not resource.is_available_schedule(start_time, end_time):
        return jsonify({'message': 'Resource is not available during the requested time.'}), 400

    existing_reservations = Reservations.query.filter_by(resource_id=resource_id).filter(
        Reservations.start_time < end_time,
        Reservations.end_time > start_time
    ).count()

    if existing_reservations >= resource.capacity:
        return jsonify({'message': 'Resource capacity exceeded for the selected time slot'}), 400
    
    new_reservation = Reservations(
        user_id=current_user.id,
        resource_id=resource_id,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify({'message': 'Reservation created successfully'}), 201


@reservations_blueprint.route('/reservations/<int:reservation_id>', methods=['GET'])
@token_required
def get_reservation(current_user, reservation_id):
    reservation = Reservations.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    reservation_data = {
        'id': reservation.id,
        'resource_id': reservation.resource_id,
        'resource_name': reservation.resource.name,
        'start_time': reservation.start_time.isoformat(),
        'end_time': reservation.end_time.isoformat()
    }
    return jsonify({'reservation': reservation_data}), 200


@reservations_blueprint.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@token_required
def delete_reservation(current_user, reservation_id):
    reservation = Reservations.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    db.session.delete(reservation)
    db.session.commit()
    return jsonify({'message': 'Reservation deleted successfully'}), 200