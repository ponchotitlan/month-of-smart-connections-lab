FROM node:20-alpine

# Small runtime image with supergateway available at container start.
RUN npm install -g supergateway

WORKDIR /app
COPY docker/start-drawio-mcp.sh /usr/local/bin/start-drawio-mcp.sh
RUN chmod +x /usr/local/bin/start-drawio-mcp.sh

ENTRYPOINT ["/usr/local/bin/start-drawio-mcp.sh"]
