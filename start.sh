echo "Hello, World! Restarting the server..."

echo "1. Terminating the process..."

pkill gunicorn

echo "Completed!"

echo "2. Starting the new process..."

gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --workers 2 --daemon

if [ $? -eq 0 ]; then
    echo "Server started successfully!"
else
    echo "Failed to start the server. Check the error logs."
    exit 1
fi

echo "Completed!"