from coarsetenancytest import CoarseTenancyTest
from porttest import PortTest
from networktest import NetworkTest
from servicetest import ServiceTest

if __name__ == "__main__":
    NetworkTest()
    PortTest()
    CoarseTenancyTest()
    ServiceTest()
