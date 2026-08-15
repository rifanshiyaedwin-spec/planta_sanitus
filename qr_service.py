import qrcode
import io
import base64

def generate_product_qr_code(product_id, product_name):
    data = f'product:{product_id}|{product_name}'
    qr = qrcode.QRCode(box_size=3, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffered = io.BytesIO()
    img.save(buffered, format='PNG')
    img_bytes = buffered.getvalue()
    data_uri = 'data:image/png;base64,' + base64.b64encode(img_bytes).decode('utf-8')
    return data_uri
