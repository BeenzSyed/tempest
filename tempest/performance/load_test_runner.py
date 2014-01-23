from eventlet import greenpool, sleep
from multiprocessing import Process


class LoadTestRunner(object):
    def __init__(self, load_pattern):
        self.load_pattern = load_pattern

    def run(self, api_caller, *args, **kwargs):
        print self.load_pattern.get_steps()
        for step in self.load_pattern.get_steps():
            processes = []
            # pool = greenpool.GreenPile()
            while step['load'] > 0:
                p = Process(target=api_caller, args=args, kwargs=kwargs)
                processes.append(p)
                p.start()
                step['load'] -= 1
            for process in processes:
                process.join()
            # for result in pool:
            #     print result
            #     print "No result to print"
            print "Step Ended. About to sleep for %s" % step['wait_time']
            sleep(step['wait_time'])
