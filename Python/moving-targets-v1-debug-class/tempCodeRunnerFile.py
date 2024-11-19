if self.t1.is_alive():
            self.t1.join(timeout=1)
        if self.t2.is_alive():
            self.t2.join(timeout=1)