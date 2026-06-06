"""
utils.py
Contains classes/functions to track AI analytics (time, expanded nodes).
"""
import time

class AIAnalytics:
    def __init__(self):
        self.nodes_expanded = 0
        self.start_time = 0
        self.end_time = 0

    def start_timer(self):
        self.start_time = time.perf_counter()
        self.nodes_expanded = 0

    def stop_timer(self):
        self.end_time = time.perf_counter()

    def increment_node(self):
        self.nodes_expanded += 1

    def get_metrics(self):
        response_time_ms = (self.end_time - self.start_time) * 1000
        return {
            "response_time_ms": round(response_time_ms, 2),
            "nodes_expanded": self.nodes_expanded
        }
