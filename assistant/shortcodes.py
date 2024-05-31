import re 
from django.middleware.csrf import get_token
from .models import ContactForms
from contactform.shortcodes import handle_contactform
def process_shortcodes(request, body):
    shortcode_handlers = {
        'form': handle_form,
        'img': handle_img,
        'contactform': handle_contactform
    }

    csrf_token = get_token(request) 
    for shortcode_type, handler in shortcode_handlers.items():
        body = handler(body, csrf_token)

    return body

def handle_form2(body, csrf_token):
    form_fields = re.findall(r'\[form(?:\s+field:([^[\]]+))?\]', body)
    for field_types_str in form_fields:
        field_types = [field.strip() for field in field_types_str.split(',')] if field_types_str else []  # Default to empty list if no field types are specified
        if not field_types:
            # For [form]
            form_html = f"""
            <form method="post" class ="max-w-md p-8">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <label for="name">Name:</label><br>
                <input class = "w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="text" id="name" name="name" required><br><br>

                <label for="message">Message:</label><br>
                <textarea class ="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" id="message" name="message" rows="4" cols="50" required></textarea><br><br>
                <input class= "w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="submit" value="Submit">
            </form>
            """
        else:
            # For [form field: ] with specific fields
            form_html = ""
            for field_type in field_types:
                # form_html += f"""
                #     <label for="{field_type}">{field_type.capitalize()}:</label><br>
                #     <input type="{field_type}" id="{field_type}" name="{field_type}" required><br><br>
                #     """
                if field_type == 'text':
                    form_html += f"""
                    <label for="{field_type}">{field_type.capitalize()}:</label><br>
                    <input type="{field_type}" id="{field_type}" name="{field_type}" required><br><br>
                    """
                elif field_type == 'textarea':
                    form_html += f"""
                    <label for="{field_type}">{field_type.capitalize()}:</label><br>
                    <textarea id="{field_type}" name="{field_type}" rows="4" cols="50" required></textarea><br><br>
                    """
                elif field_type == 'checkbox':
                    form_html += f"""
                    <input type="{field_type}" id="{field_type}" name="{field_type}" required>
                    """
              
            form_html += f"""
            <input type="submit" value="Submit">
            </form>
            """
        body = re.sub(r'\[form(?:\s+field:' + re.escape(field_types_str) + r')?\]', form_html, body, count=1)

    return body
# class placeholder 

def handle_img(body, csrf_token):
    img_htmls = {}
    img_tags = re.findall(r'\[img src:"([^"]+)"\]', body)
    if img_tags:
        for img_src in img_tags:
            img_htmls[img_src] = f'<img src="{img_src}" alt="image">'

    for img_src, img_html in img_htmls.items():
        body = re.sub(r'\[img src:"' + re.escape(img_src) + r'"\]', img_html, body)
    return body

# def handle_contactform(body, csrf_token):
#     contact_forms = {}
#     contact_form_id = re.findall(r'\[contactform id:(\d+)\]', body)
#     # form_id = int(contact_form_id[0])
#     default_contact_form = f"""
                            
#                             <form method="post" class ="max-w-md p-8">
#                             <p> Contact form </p>
#                                 <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
#                                 <label for="name">Name:</label><br>
#                                 <input class = "w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="text" id="name" name="name" required><br><br>

#                                 <label for="message">Contact :</label><br>
#                                 <textarea class ="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" id="message" name="message" rows="4" cols="50" required></textarea><br><br>
#                                 <input class= "w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="submit" value="Submit">
#                             </form>
#                             """

#     if contact_form_id:
#         for form_id in contact_form_id:
#             if form_id not in contact_forms:
#                 try:
#                     contact_form = ContactForms.objects.get(id=form_id).form_html
#                     f"""
                            
#                             <form method="post" class ="max-w-md p-8" action='#'>
#                             {contact_form}
#                             </form>
#                             """
#                 except ContactForm.DoesNotExist:
#                     # contact_form = default_contact_form
#                     contact_form = f"""<span style='color: red;'> <em>The form with id {form_id} does not exist</em></span>"""
#                 contact_forms[form_id] = f"{contact_form}"
               
#     for form_id, form_html in contact_forms.items():
#         body = re.sub(r'\[contactform id:' + re.escape(form_id) + r'\]', form_html, body)
#     body = re.sub(r'\[contactform\]', default_contact_form, body)
#     return body



# def handle_form(body, csrf_token):
#     form_fields = re.findall(r'\[form(?:\s+field:([^[\]]+))?\]', body)
#     csrf_token = csrf_token
#     for field_types_str in form_fields:
#         if not field_types_str:
#             # For [form]
#             form_html = """
#             <form method="post" class ="max-w-md p-8">
#                 <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
#                 <label for="name">Name:</label><br>
#                 <input class="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="text" id="name" name="name" required><br><br>

#                 <label for="message">Message:</label><br>
#                 <textarea class="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" id="message" name="message" rows="4" cols="50" required></textarea><br><br>
#                 <input class="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="submit" value="Submit">
#             </form>
#             """
#         else:
#             # For [form field: ] with specific fields
#             field_defs = field_types_str.split(',')
#             field_specs = [field_def.strip() for field_def in field_defs]
#             form_html = ""
           
#             for field_spec in field_specs:
#                 # field_match = re.match(r'(\w+)\((\w+)\)', field_spec)
#                 field_match = re.match(r'(\w+)\(([^)]+)\)', field_spec)
#                 if field_match:
#                     field_type = field_match.group(1)
#                     field_label = field_match.group(2)
#                 else:
#                     field_type = field_spec
#                     field_label = field_spec

                
#                 form_html += f"""
#                              <form method="post" action="/test/">
#                              <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
#                              """
                # if field_type == 'text':
                #     form_html += f"""
                #     <label for="{field_label}">{field_label.capitalize()}:</label><br>
                #     <input type="{field_type}" id="{field_label}" name="{field_label}" required><br><br>
                #     """
                # elif field_type == 'textarea':
                #     form_html += f"""
                #     <label for="{field_label}">{field_label.capitalize()}:</label><br>
                #     <textarea id="{field_label}" name="{field_label}" rows="4" cols="50" required></textarea><br><br>
                #     """
                # elif field_type == 'checkbox':
                #     form_html += f"""
                #     <input type="{field_type}" id="{field_label}" name="{field_label}" required>
                #     <label for="{field_label}">{field_label.capitalize()}</label><br><br>
#                     """
#             form_html += f"""
#                 <input type="submit" value="Submit">
#                 </form>
#                 """
#         body = re.sub(r'\[form(?:\s+field:' + re.escape(field_types_str) + r')?\]', form_html, body)

#     return body


def handle_form(body, csrf_token):
    shortcode_pattern = r'\[form(?:\s+field:(.*?)\s*(?:class:(.*?))?)?\]'
    
    matches = re.findall(shortcode_pattern, body)
    
    for field_types_str, class_attr_str in matches:
        form_html = "<form method='post'>"
        
        if field_types_str:
            fields = [field.strip() for field in field_types_str.split(',')]
            
            for field in fields:
                if '(' in field:
                    field_type, field_label = field.split('(')
                    field_label = field_label[:-1]  # Remove the closing parenthesis
                else:
                    field_type = field
                    field_label = field
                if field_type == 'text':
                    form_html += f"""
                    <label for="{field_label}">{field_label.capitalize()}:</label><br>
                    <input type="{field_type}" id="{field_label}" name="{field_label}" {f'class="{class_attr_str}"' if class_attr_str else None}><br><br>
                    """
                elif field_type == 'textarea':
                    form_html += f"""
                    <label for="{field_label}">{field_label.capitalize()}:</label><br>
                    <textarea id="{field_label}" name="{field_label}" {f'class="{class_attr_str}"' if class_attr_str else None}></textarea><br><br>
                    """
                elif field_type == 'checkbox':
                    form_html += f"""
                    <input type="{field_type}" id="{field_label}" name="{field_label}" {f'class="{class_attr_str}"' if class_attr_str else None}><br><br>
                    <label for="{field_label}">{field_label.capitalize()}</label><br><br>


                    """
        # Add CSRF token field
        form_html += f"<input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>"
        
        # Add submit button and close the form
        form_html += f"""
        <input type="submit" id="submit" name="submit" value="submit" {f'class="{class_attr_str}"' if class_attr_str else None}><br><br>
        </form>
        """
        print(form_html)
        # Replace the shortcode with the generated HTML in the body
        body = re.sub(re.escape(f'[form{" field:" + field_types_str if field_types_str else ""}{" class:" + class_attr_str if class_attr_str else ""}]'), form_html, body)
    
    return body