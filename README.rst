.. _Python: https://www.python.org/
.. _virtualenv: https://pypy.python.org/pypi/virtualenv
.. _virtualenvwrapper: https://pypy.python.org/pypi/virtualenvwrapper


Minimal JavaScript Interpreter
==============================

This is a minimal JavaScript Interpreter based off
`kostialopuhin/jss-interp <https://bitbucket.org/kostialopuhin/jss-interp>`_
and tidied up a bit with some opinionated conventions, documentation and
project infrastructure.


Prerequisites
-------------

It's recommended that you do all development using a Python Virtual
Environment using `virtualenv`_ and/or using the nice `virtualenvwrapper`_.

::
    
    $ mkvirtualenv jslang

You will need the `RPython <https://bitbucket.org/pypy/pypy>`_ toolchain
to build the interpreter. The easiest way to do this is to
`My Fork of PyPy <https://bitbucket.org/prologic/pypy>`_ which includes
a convenient ``setup-rpython.py`` to make working with the RPython toolchain
a bit easier.

::
    
    $ hg clone https://bitbucket.org/prologic/pypy
    $ cd pypy
    $ python setup-rpython.py develop


Installation
------------

Grab the source from https://bitbucket.org/prologic/js-lang and either
run ``python setup.py develop`` or ``pip install -r requirements.txt``

::
    
    $ hg clone https://bitbucket.org/prologic/js-lang
    $ cd js-lang
    $ pip install -r requirements.txt


Building
--------

To build the interpreter simply run ``js/target.py`` against the RPython
Compiler.

::
    
    $ rpython --output=jsc js/target.py


Usage
-----

You can either run the interpreter using `Python`_ itself or running the
compiled interpreter ``jsc``.

::
    
    $ js examples/fib.js
    $ jsc examples/fib.js
