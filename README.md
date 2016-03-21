## Getting Started with XOS and CORD

For a general introduction to XOS and how it is used in CORD, see
http://guide.xosproject.org. The "Developer Guide" at that URL is
especially helpful, although it isn't perfectly sync'ed with master. 
Additional design notes, presentations, and other collateral are 
also available at http://xosproject.org and http://opencord.org.

The best way to get started is to look at the collection of
canned configurations in `xos/configurations/`. The `cord` 
configuration in that directory corresponds to our current 
CORD development environment, and the `README.md` you'll find there
will help you get started.

Source tree layout:
 * applications -- stand-alone applications that run on top of XOS.
 * containers -- common Dockerfiles used by various XOS configurations
 * views -- mechanisms to extend XOS with customized views
 * xos -- XOS internals
