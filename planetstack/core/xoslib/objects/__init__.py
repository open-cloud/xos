from .slivers import XOSSlivers
from .sites import XOSSites
from .nodes import XOSNodes
from .slices import XOSSlices

XOSLIB_OBJECTS = {}

XOSLIB_OBJECTS[XOSSlivers.name] = XOSSlivers
XOSLIB_OBJECTS[XOSSites.name] = XOSSites
XOSLIB_OBJECTS[XOSNodes.name] = XOSNodes
XOSLIB_OBJECTS[XOSSlices.name] = XOSSlices

