from main import app, IP

if __name__ == "__main__":
    app.run(host=IP, port=8443, use_reloader=True,
            debug=True, ssl_context=('webhook_cert.pem', 'webhook_pkey.pem'))
