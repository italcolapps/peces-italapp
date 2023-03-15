import base64
logo = 'Imagenes/banner_peces.png'
logo_encoded = base64.b64encode(open(logo, 'rb').read())


logo_reporte = 'Imagenes/banner_peces.png'
logo_reporte_encoded = base64.b64encode(open(logo_reporte, 'rb').read())