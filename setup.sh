mkdir -p ~/.streamlit

echo "[server]
headless = true
port = $PORT
enableCORS = false
[theme]
base = "light"
" > ~/.streamlit/config.toml