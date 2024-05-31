import base64


def encode_data(data):
    id_bytes = str(data).encode('utf-8')
    encoded_data = base64.urlsafe_b64encode(id_bytes).decode('utf-8')
    return encoded_data

def decode_data(encoded_data):
    decoded_bytes = base64.urlsafe_b64decode(encoded_data.encode('utf-8'))
    decoded_data = int(decoded_bytes.decode('utf-8'))
    return decoded_data