FROM golang:1.24.1-alpine

WORKDIR /app
COPY . .

RUN go mod tidy && go build -o agent-daemon .

CMD ["./agent-daemon"]
