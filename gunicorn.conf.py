import multiprocessing


bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "-"
loglevel = "info"
capture_output = True
keepalive = 1000
timeout = 1000
worker_class = "gevent"
# logger_class = "hm_api.app.InterceptHandler"
