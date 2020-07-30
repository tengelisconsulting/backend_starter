#!/usr/bin/env python3

import logging
import os
import subprocess
import time


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
SERVICE_WAIT_S = int(os.environ.get("SERVICE_WAIT_S", 2))


SUCCESS_MSG = """
+---------------------------------------------------------------------------+
|                              TESTS PASSED                                 |
+---------------------------------------------------------------------------+
"""


def run_integration_tests():
    logging.info("wait for services...")
    time.sleep(SERVICE_WAIT_S)
    logging.info("running integration tests...")
    integration_dir = os.path.join(TEST_DIR, "integration")
    test_output = subprocess.check_output(
        ["find", integration_dir, "-maxdepth", "1", "-name", "*_test.py"]
    ).decode("utf-8")
    tests = [t for t in test_output.split("\n") if t]
    for t in tests:
        logging.info("  -- running test %s", t)
        res = subprocess.run(["python3", t],
                             env=os.environ)
        if res.returncode != 0:
            logging.error("test failed %s", t)
            logging.error(res.stderr)
            raise Exception("INTEGRATION TESTS FAILED")
    logging.info("---------- INTEGRATION TESTS PASSED ----------")
    return


def run_noauto_tests():
    logging.info("NO NOAUTO TESTS CONFIGURED NOW")
    return
#     logging.info("running noauto tests...")
#     test_output = subprocess.check_output(
#         ["find", "./tests", "-maxdepth", "1", "-name", "*_test_noauto.py"]
#     ).decode("utf-8")
#     tests = [t for t in test_output.split("\n") if t]
#     for t in tests:
#         res = subprocess.run(["python3", t],
#                              env=os.environ)
#         if res.returncode != 0:
#             logging.error("test failed: %s", t)
#             logging.error(res.stderr)
#             raise Exception("NOAUTO TESTS FAILED")
#     logging.info("---------- NOAUTO TESTS PASSED ----------")
#     return


def run_worker_test(worker_name: str):
    logging.info("---------- TESTING WORKER %s ----------", worker_name)
    test_path = os.path.join(TEST_DIR, "workers",
                             "{}_test_w.py".format(worker_name))
    res = subprocess.run(["python3", test_path])
    if res.returncode != 0:
        logging.error("worker %s tests failed", worker_name)
        logging.error(res.stderr)
        msg = "WORKER TESTS FAILED - {}".format(worker_name)
        raise Exception(msg)
    logging.info("---------- WORKER %s TESTS PASSED ----------", worker_name)
    return


def main():
    logging.basicConfig(level=logging.INFO)
    import sys
    if len(sys.argv) < 2:
        run_integration_tests()
        return
    mode = sys.argv[1]
    if mode == "noauto":
        run_noauto_tests()
    elif mode == "w":
        worker_name = sys.argv[2]
        run_worker_test(worker_name)
    else:
        logging.error("no such mode: %s", mode)
    return


if __name__ == "__main__":
    main()
