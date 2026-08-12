def test_start_succeeds_on_200(client, requests_mock):
    requests_mock.post(f"{client.base_url}/api/panic/start", status_code=200)

    client.panic.start()


def test_stop_succeeds_on_200(client, requests_mock):
    requests_mock.post(f"{client.base_url}/api/panic/stop", status_code=200)

    client.panic.stop()
