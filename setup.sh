mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"james@seoworks.co.uk\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
enableCors = true" >> ~/.streamlit/config.toml
