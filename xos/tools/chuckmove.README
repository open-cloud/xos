Hi,

I've written a tool called 'chuckmove' for helping move Python modules around in a source tree. You use it as follows. Lets say you want to relocate a module to a different location in the tree, and also rename it. So for instance, x is to become y.z. The syntax you use is:

chuckmove -o x -n y.z <root directory>

Invoking this command makes the tool recursively descend into the root directory, make a backup copy of each file (adding the prefix '.orig') and rewrite the imports in it, so that "import x" gets turned into "import y.z"

It recognizes Python grammar, so it works with all of these forms:

from x import a
from x.b import c 
import x.d.e.f as foo # Comments are also handled

...with the nit that lines with syntax/grammatical errors are left as is.

For example, for the observer/synchronizer changes, I just had to do the following:

chuckmove -o observer -n synchronizers.base xos

...and then to generate a patch with the changes:

gendiff xos .orig

It's checked into the xos repository under tools (with a README file!).

Sapan
