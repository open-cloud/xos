from enginetest import EngineTest
from coarsetenancytest import CoarseTenancyTest
from porttest import PortTest
from networktest import NetworkTest
from servicetest import ServiceTest
from usertest import UserTest
from computetest import ComputeTest
from sitetest import SiteTest
from deploymenttest import DeploymentTest
from nodetest import NodeTest
from slicetest import SliceTest
from controllertest import ControllerTest
from imagetest import ImageTest

if __name__ == "__main__":
    EngineTest()
    SiteTest()
    DeploymentTest()
    ControllerTest()
    NodeTest()
    NetworkTest()
    PortTest()
    CoarseTenancyTest()
    ServiceTest()
    UserTest()
    SliceTest()
    ComputeTest()
    ImageTest()
