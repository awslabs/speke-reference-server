import os
import datetime
import pytest
from .helpers.generate_test_artifacts import TestFileGenerator


def pytest_addoption(parser):
    parser.addoption("--speke-url", help="Speke Key provider URL")
    parser.addoption("--skip-artifact-generation", help="Skip generation of test artifacts", action='store_true')
    parser.addoption("--vod", help="Generated request won't contain ContentKeyPeriodList", action='store_true')


@pytest.fixture(scope="session", autouse=True)
def spekev2_url(request):
    """
    Example: "https://<api-gateway-id>.execute-api.<aws-region>.amazonaws.com/EkeStage/copyProtection"
    """
    return request.config.getoption("--speke-url")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # Create a report folder and configure report name
    configure_report_options(config)

    # Create artifacts used in the test suite
    if config.getoption("--skip-artifact-generation"):
        print("Skipping test artifact generation")
    else:
        TestFileGenerator().generate_artifacts()

    if config.getoption("--vod"):
        TestFileGenerator().isLive = False

def configure_report_options(config):
    date_now = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S").replace(" ", "_")
    if not os.path.exists('reports'):
        os.makedirs('reports')
    config.option.htmlpath = 'reports/test_results_' + date_now + ".html"
