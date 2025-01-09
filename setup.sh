mkdir -p ~/.streamlit

echo "[server]
headless = true
port = $PORT
enableCORS = false
[theme]
base = 'light'
[client]
showErrorDetails=false
sslCertFile = '/SSL/ssl.pdumitradome.id.pem'
sslKeyFile = 'SSL/ssl.pdumitradome.id.key'
" > ~/.streamlit/config.toml