FROM node:20-alpine

# Small runtime image with supergateway available at container start.
RUN npm install -g supergateway

WORKDIR /app
COPY docker/start-github-mcp.sh /usr/local/bin/start-github-mcp.sh
RUN chmod +x /usr/local/bin/start-github-mcp.sh

ENTRYPOINT ["/usr/local/bin/start-github-mcp.sh"]
