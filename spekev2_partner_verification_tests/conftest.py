import os
import datetime
import pytest


def pytest_addoption(parser):
    parser.addoption("--speke-url", help="Speke Key provider URL")


@pytest.fixture(scope="session", autouse=True)
def spekev2_url(request):
    """
    Example: "https://<api-gateway-id>.execute-api.us-west-2.amazonaws.com/EkeStage/copyProtection"
    """
    return request.config.getoption("--speke-url")

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    date_now = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S").replace(" ", "_")
    if not os.path.exists('reports'):
        os.makedirs('reports')
    config.option.htmlpath = 'reports/test_results_'+date_now+".html"
  