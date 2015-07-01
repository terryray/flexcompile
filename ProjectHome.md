This is a single python script that invokes the "fcsh" utility for you.  It gives you all the benefits of fcsh while also letting you use make or other similar tools to define how to build your project.  Make a change, type make, your code gets recompiled with the speed benefit of fcsh, and without you having to keep fcsh running in a separate window and typing "compile 1" at it.

Installation is simple: just put flexcompile.py in your path somewhere.  Then you can compile your stuff by putting "flexcompile.py" in your command line, right in front of mxmlc.  For example:

> flexcompile.py fcsh mxmlc myproject.mxml

Doing it the first time is  nothing special.  The second time you run it, you will find things are much faster, especially if you have a largish flex project.

This works by invisibly forking off a daemon process that runs fcsh for you.