wsgi_app = "Instanssi.wsgi:application"
bind = "127.0.0.1:8006"
workers = 3
proc_name = "instanssi"
max_requests = 1000
max_requests_jitter = 10
