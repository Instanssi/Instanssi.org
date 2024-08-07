wsgi_app = "Instanssi.asgi:application"
bind = "127.0.0.1:8006"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
proc_name = "instanssi"
max_requests = 4000
max_requests_jitter = 50
capture_output = True
errorlog = "/var/log/instanssi/gunicorn.error.log"
accesslog = "/var/log/instanssi/gunicorn.access.log"
