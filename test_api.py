import json
import socket
import threading
import time
import unittest
import urllib.request
import urllib.parse
import urllib.error

TEST_PORT = 8082

def _run_test_server():
    from urllib.parse import unquote
    from dice_model import Dice

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('localhost', TEST_PORT))
    srv.listen(5)
    srv.settimeout(1.0)

    def make_json(data, status="200 OK"):
        body = json.dumps(data)
        return f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\n\r\n{body}"

    def parse_qs(path):
        params = {}
        if "?" in path:
            qs = unquote(path.split("?", 1)[1])
            for pair in qs.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = v
        return params

    while _server_running:
        try:
            conn, _ = srv.accept()
        except socket.timeout:
            continue

        req = conn.recv(2048).decode('utf-8')
        first_line = req.split("\n")[0]
        path = first_line.split(" ")[1] if len(first_line.split(" ")) > 1 else "/"

        if path.startswith("/roll_dice"):
            try:
                params = parse_qs(path)
                probs = list(map(float, params["probabilities"].split(",")))
                n = int(params["number"])
                dice = Dice(probabilities=probs, num_rolls=n)
                result = dice.roll()
                resp = make_json({"status": "success", **result.to_dict()})
            except Exception as e:
                resp = make_json({"status": "error", "error": str(e)}, "400 Bad Request")
        elif path.startswith("/myjson"):
            resp = make_json({"status": "success", "message": "Hello, KU!"})
        else:
            resp = "HTTP/1.1 404 Not Found\r\n\r\n"

        conn.sendall(resp.encode('utf-8'))
        conn.close()

    srv.close()


_server_running = True
_server_thread = threading.Thread(target=_run_test_server, daemon=True)


def _get(path: str) -> dict:
    url = f"http://localhost:{TEST_PORT}{path}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode())


def _get_error(path: str):
    url = f"http://localhost:{TEST_PORT}{path}"
    try:
        urllib.request.urlopen(url, timeout=5)
        raise AssertionError("Expected HTTPError but request succeeded")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        return e.code, body


class TestRollDiceEndpoint(unittest.TestCase):

    def test_status_success(self):
        data = _get("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=10")
        self.assertEqual(data["status"], "success")

    def test_results_length_matches_number(self):
        data = _get("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=15")
        self.assertEqual(len(data["results"]), 15)

    def test_results_values_in_valid_range(self):
        data = _get("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=50")
        for face in data["results"]:
            self.assertIn(face, [1, 2, 3, 4, 5, 6])

    def test_response_contains_counts(self):
        data = _get("/roll_dice?probabilities=1,0,0,0,0,0&number=5")
        self.assertIn("counts", data)

    def test_response_contains_frequencies(self):
        data = _get("/roll_dice?probabilities=1,0,0,0,0,0&number=5")
        self.assertIn("frequencies", data)

    def test_num_rolls_in_response(self):
        data = _get("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=7")
        self.assertEqual(data["num_rolls"], 7)

    def test_deterministic_face_with_prob_one(self):
        data = _get("/roll_dice?probabilities=1,0,0,0,0,0&number=20")
        self.assertTrue(all(f == 1 for f in data["results"]))

    def test_uniform_distribution_single_roll(self):
        data = _get("/roll_dice?probabilities=0.16667,0.16667,0.16667,0.16667,0.16667,0.16665&number=1")
        self.assertEqual(data["num_rolls"], 1)
        self.assertIn(data["results"][0], [1, 2, 3, 4, 5, 6])

    def test_counts_sum_equals_number(self):
        n = 30
        data = _get(f"/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number={n}")
        counts = data["counts"]
        self.assertEqual(sum(counts.values()), n)

    def test_missing_probabilities_param(self):
        code, body = _get_error("/roll_dice?number=5")
        self.assertEqual(code, 400)
        self.assertIn("error", body)

    def test_missing_number_param(self):
        code, body = _get_error("/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1")
        self.assertEqual(code, 400)
        self.assertIn("error", body)

    def test_wrong_number_of_probabilities(self):
        code, body = _get_error("/roll_dice?probabilities=0.5,0.5&number=5")
        self.assertEqual(code, 400)
        self.assertIn("error", body)

    def test_probabilities_not_summing_to_one(self):
        code, body = _get_error(
            "/roll_dice?probabilities=0.2,0.2,0.2,0.2,0.2,0.5&number=5"
        )
        self.assertEqual(code, 400)
        self.assertIn("error", body)

    def test_invalid_number_value(self):
        code, body = _get_error(
            "/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=abc"
        )
        self.assertEqual(code, 400)

    def test_negative_num_rolls(self):
        code, body = _get_error(
            "/roll_dice?probabilities=0.1,0.2,0.3,0.1,0.2,0.1&number=-1"
        )
        self.assertEqual(code, 400)


class TestMyjsonEndpoint(unittest.TestCase):

    def test_myjson_status(self):
        data = _get("/myjson")
        self.assertEqual(data["status"], "success")

    def test_myjson_message(self):
        data = _get("/myjson")
        self.assertIn("message", data)


def setUpModule():
    global _server_running
    _server_running = True
    _server_thread.start()
    time.sleep(0.3)


def tearDownModule():
    global _server_running
    _server_running = False
    _server_thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)