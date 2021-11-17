import tornado.ioloop
import tornado.web
import drift_collector
import threading
import time
import json
from datetime import datetime


def reduce(whole, reduce_to=1000):
    """reduce number of entries in list by skipping"""
    reducer = int(len(whole) / reduce_to)
    reduced = whole[::reducer]
    return reduced


def to_ts(date_strings):
    timestamps = []
    for key in date_strings:
        timestamp = datetime.timestamp(datetime.strptime(key, "%Y-%m-%d %H:%M:%S+00:00"))
        timestamps.append(int(timestamp))
    return timestamps


class ChartHandler(tornado.web.RequestHandler):
    def get(self):
        input_dict = drift_collector.read_input()["data"]

        print(input_dict.keys())

        values_full = []

        for key in input_dict.keys():
            print(input_dict[key]["drift"])
            values_full.append(input_dict[key]["drift"])
            print(input_dict[key]["drift"])
        print(values_full)

        labels_full = input_dict.keys()

        values = reduce(list(values_full))
        labels = reduce(list(labels_full))

        self.render("chart.html",
                    labels=json.dumps(labels),
                    values=json.dumps(values)
                    )


class ChartRecentHandler(tornado.web.RequestHandler):
    def get(self):
        input_dict = drift_collector.read_input()

        block_max = input_dict["stats"]["last_block"]
        block_min = block_max - 1000
        block_range = range(block_min, block_max)

        print(block_max)

        x_list = []
        for key in input_dict.keys():
            print(key)
            if int(key) >= block_min:
                x_list.append(key)

        print(x_list)

        self.render("chart.html",
                    labels=json.dumps(""),
                    values=json.dumps("")
                    )


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(drift_collector.read_input())


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/chart", ChartHandler),
        (r"/chart_recent", ChartRecentHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])


class ThreadedClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            drift_collector.collect()
            time.sleep(60)


if __name__ == "__main__":
    background = ThreadedClient()
    background.start()
    print("Background process started")

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
