import re 
import base64
from .models import ContactForm
from django.middleware.csrf import get_token
from .utils import encode_data


def handle_contactform(body, csrf_token):
    csrf_token = csrf_token
    contact_forms = {}
    contact_form_id = re.findall(r'\[contactform id:(\d+)\]', body)
    # form_id = int(contact_form_id[0])
 
    default_contact_form = f"""
                            
                            <form method="post" action='/contactform/test/'>
                            <p> Contact form </p>
                                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                <label for="name">Name:</label><br>
                                <input class = "w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="text" id="name" name="name" required><br><br>

                                <label for="message">Contact :</label><br>
                                <textarea class ="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" id="message" name="message" rows="4" cols="50" required></textarea><br><br>
                                <input class= "w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary" type="submit" value="Submit">
                            </form>
                            """

    if contact_form_id:
        for form_id in contact_form_id:
            if form_id not in contact_forms:
                try:
                    contact_form = ContactForm.objects.get(id=form_id).form_html
                    encoded_id = encode_data(form_id)                 
                except ContactForm.DoesNotExist:
                   
                    contact_form = f"""<span style='color: red;'> <em>The form with id {form_id} does not exist</em></span>"""
                contact_forms[form_id] = f"""
                            
                            <form method="post" class ="max-w-md p-8" action='/contactform/handleform/'>
                            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                            <input type="hidden" name="form" value="{encoded_id}">


                            {contact_form}
                            </form>
                            """
               
    for form_id, form_html in contact_forms.items():
        body = re.sub(r'\[contactform id:' + re.escape(form_id) + r'\]', form_html, body)
    body = re.sub(r'\[contactform\]', default_contact_form, body)
    return body
