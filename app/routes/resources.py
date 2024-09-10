from flask import Blueprint, jsonify
from app.models import Resource
from app.services.auth_service import token_required

resources_blueprint = Blueprint("resources", __name__)

@resources_blueprint.route("/resources", methods=["GET"])
@token_required
def get_resources(current_user):
    resources = Resource.query.all()
    output = []
    for resource in resources:
        resource_data = {
            "id": resource.id,
            "name": resource.name,
            "description": resource.description,
            "capacity": resource.capacity,
            "schedule": resource.schedule
        }
        output.append(resource_data)
    return jsonify({"resources": output}), 200


@resources_blueprint.route("/resources/<int>:resource_id", methods=["GET"])
@token_required
def get_resource(current_user, resource_id):
    resource = Resource.query.get_or_404(resource_id)
    resource_data = {
        'id': resource.id,
        'name': resource.name,
        'description': resource.description,
        'capacity': resource.capacity,
        'schedule': resource.schedule
    }
    return jsonify({"resource": resource_data}), 200