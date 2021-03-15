from flask import Blueprint, render_template, request

mass_detect = Blueprint('mass_detect', __name__, template_folder='templates')

@mass_detect.route('/plugin/mass_detect/<reports.json>', methods = ['POST'])
def mass_detect():
   content = request.get_json
   print(content)