mkdir -p ~/.streamlit

echo "[server]
headless = true
port = $PORT
enableCORS = false
sslCertFile = 'SSL/ssl.pdumitradome.id.pem'
sslKeyFile = 'SSL/ssl.pdumitradome.id.key'
[theme]
base = 'light'
[client]
showErrorDetails=false


" > ~/.streamlit/config.toml