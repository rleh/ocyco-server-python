from flask import Blueprint, jsonify, request

from werkzeug.exceptions import abort
from app import db

from app.profiles.models import Profiles
from app.way_types.models import WayTypes  # create way_types table (static_cost table depends on it)
from app.cost_static.models import CostStatic


mod = Blueprint('profile', __name__)

# TODO: validate language tag
# TODO: unknown language error handling


@mod.route('/profiles', methods=['GET'])
def profiles_list():
    """
    List all profiles
    """
    # Read JSON from request
    json = request.get_json()
    # language (default is 'de-DE')
    language = 'de-DE'
    # Check for lang fields present
    if (json is not None) and (not ('lang' in json)):
        language = json.get('lang')
    profile_list = {}
    for profile in Profiles.query.all():
        profile_list[profile.get_name()] = profile.get_description(language)
    return jsonify(profile_list)


@mod.route('/profiles/<string:profile_name>', methods=['GET'])
def profile_get(profile_name):
    """
    Get a profile by name inclusive costs
    """
    # Read JSON from request
    json = request.get_json()
    language='de-DE'
    # Check for lang fields present
    if (json is not None) and (not ('lang' in json)):
        language = json.get('lang')
    profile = Profiles.query.filter(Profiles.name == profile_name).first()
    return jsonify(profile.to_dict_long(language))


@mod.route('/profiles/<string:profile_name>', methods=['POST'])
def profile_update(profile_name):
    """
    Update profiles cost
    """
    profile_id = Profiles.query.filter_by(name=profile_name).first().id
    way_types_rows = WayTypes.query.all()
    way_types = []
    for row in way_types_rows:
        way_types.append(int(row.id))
    json = request.get_json()
    if json is None:
        abort(400, 'JSON body missing')
    for cost_id in json:
        if not int(cost_id) in way_types:
            abort(400, 'unknown way_type id: ' + cost_id)
        cost = CostStatic.query.filter_by(profile=profile_id, id=cost_id).first()
        if ('forward' in json.get(cost_id)) and ('reverse' in json.get(cost_id)):
            cost.cost_forward = json.get(cost_id).get('forward')
            cost.cost_reverse = json.get(cost_id).get('reverse')
        else:
            try:
                cost_value = float(json.get(cost_id))
                cost.cost_forward = cost_value
                cost.cost_reverse = cost_value
            except ValueError:
                abort(400, 'bad cost value for way_type ' + cost_id)
        db.session.commit()
    return '', 204
