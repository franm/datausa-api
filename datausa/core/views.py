from flask import Blueprint, request, jsonify
from datausa.attrs.models import Course, Naics, University
from datausa.core import table_manager
from datausa.core import api

mod = Blueprint('core', __name__, url_prefix='/api')

manager = table_manager.TableManager()

def show_attrs(attr_obj):
    attrs = attr_obj.query.all()
    data = [a.serialize() for a in attrs]
    return jsonify(data=data)

def get_prereqs():
    show = request.args.get("show", "")
    sumlevel = request.args.get("sumlevel", "")
    value = request.args.get("value", "")

    shows = show.split(",")
    sumlevels = sumlevel.split(",")
    values = value.split(",") if value else [] 

    shows_and_levels = {val:sumlevels[idx] for idx, val in enumerate(shows)}

    variables = manager.possible_variables
    vars_and_vals = {var:request.args.get(var, None) for var in variables}
    vars_and_vals = {k:v for k,v in vars_and_vals.items() if v}

    vars_needed = vars_and_vals.keys() + [show] + values
    return vars_needed, shows_and_levels

@mod.route("/")
def api_view():
    vars_needed, shows_and_levels = get_prereqs()
    table = manager.find_table(vars_needed, shows_and_levels)
    data = api.query(table, vars_and_vals, shows_and_levels, values=values)

    return data

@mod.route("/logic/")
def logic_view():
    vars_needed, shows_and_levels = get_prereqs()
    table_list = manager.all_tables(vars_needed, shows_and_levels)
    return jsonify(tables=[table.info() for table in table_list])