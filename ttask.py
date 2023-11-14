import re
import validate_email_address
from flask import Flask, request, jsonify

app = Flask(__name__)


form_templates = [
    {"name": "MyForm", "fields": {"user_name": "text", "order_date": "date"}},
    {"name": "Order Form", "fields": {"user_name": "text", "lead_email": "email"}},
]

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if re.match(email_regex, email):
        if validate_email_address.validate_email(email, verify=True):
            return True
        else:
            print("Invalid domain or DNS records not found.")
    else:
        print("Invalid email format.")

    return False


def validate_phone(value):
    return value.startswith("+7") and len(value) == 12

def validate_date(date_string):
    # Define the regular expression pattern
    date_pattern = re.compile(r'^(0[1-9]|[12][0-9]|3[01])[-.](0[1-9]|1[0-2])[-.](\d{4})$')

    # Check if the date_string matches the pattern
    match = date_pattern.match(date_string)

    if match:
        day, month, year = map(int, match.groups())
        if month in {1, 3, 5, 7, 8, 10, 12} and day > 31:
            return False
        elif month in {4, 6, 9, 11} and day > 30:
            return False
        elif month == 2:
            # every 4 years is leap
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                if day > 29:
                    return False
            elif day > 28:
                return False
        return True
    else:
        return False

def validate_text(value):
    return isinstance(value, str)

def validate_field(template_field_type, value):
    if template_field_type == 'email':
        return validate_email(value)
    elif template_field_type == 'phone':
        return validate_phone(value)
    elif template_field_type == 'date':
        return validate_date(value)
    elif template_field_type == 'text':
        return validate_text(value)
    else:
        return False  

def find_matching_template(data):
    for template in form_templates:
        template_fields = template['fields']
        if all(field_name in data and validate_field(template_fields.get(field_name), data[field_name]) for field_name in data):
            return template['name']
    return None

@app.route('/get_form', methods=['POST'])
def get_form():
    data = request.form.to_dict()
    template_name = find_matching_template(data)
    
    if template_name:
        return jsonify({"template_name": template_name})
    else:
        return jsonify({"error": "No matching template found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
