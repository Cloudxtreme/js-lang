.. _Python: https://www.python.org/
.. _virtualenv: https://pypy.python.org/pypi/virtualenv
.. _virtualenvwrapper: https://pypy.python.org/pypi/virtualenvwrapper
.. _Docker: https://docker.com/
.. _Latest Releases: https://github.com/prologic/js-lang/releases


Minimal JavaScript Interpreter
==============================

.. image:: https://travis-ci.org/prologic/js-lang.svg
   :target: https://travis-ci.org/prologic/js-lang
   :alt: Build Status

.. image:: https://coveralls.io/repos/prologic/js-lang/badge.svg
   :target: https://coveralls.io/r/prologic/js-lang
   :alt: Coverage

.. image:: https://codeclimate.com/github/prologic/js-lang/badges/gpa.svg
   :target: https://codeclimate.com/github/prologic/js-lang
   :alt: Code Climate

This is a minimal JavaScript Interpreter based off
`kostialopuhin/jss-interp <https://bitbucket.org/kostialopuhin/jss-interp>`_
and tidied up a bit with some opinionated conventions, documentation and
project infrastructure as well as several new features.


Prerequisites
-------------

It is recommended that you do all development using a Python Virtual
Environment using `virtualenv`_ and/or using the nice `virtualenvwrapper`_.

::
   
    $ mkvirtualenv js-lang


Installation
------------

Grab the source from https://github.com/prologic/js-lang and either
run ``python setup.py develop`` or ``pip install -e .``

::
    
    $ git clone https://github.com/prologic/js-lang.git
    $ cd js-lang
    $ pip install -e .


Building
--------

To build the interpreter simply run ``js/main.py`` against the RPython
Compiler. There is a ``Makefile`` that has a default target for building
and translating the interpreter.

::
    
    $ make

You can also use `Docker`_ to build the interpreter:

::
    
    $ docker build -t js .


Usage
-----

You can either run the interpreter using `Python`_ itself or by running the
compiled interpreter ``./bin/js``.

::
    
    $ ./bin/js examples/hello.js

Untranslated running on top of `Python`_ (*CPython*):

::
    
    $ js examples/hello.js


Grammar
-------

The grammar of js-lang is currently as follows:

::
   

    IGNORE: "[ \t\n]";

    NUMBER: "0\.?[0-9]*|[1-9][0-9]*\.?[0-9]*|\.[0-9]+";
    STRING: "\"([^\"\\]|\\.)*\"";

    ADD_OPER: "[+-]";
    MULT_OPER: "[*/%]";
    COMP_OPER: "(==)|(>=)|(<=)|>|<|(!=)";

    VARIABLE: "[a-zA-Z_][a-zA-Z0-9_]*";

    main: statement* [EOF];

    statement:
          expr ";"
        | VARIABLE "=" expr ";"
        | "while" "(" expr ")" "{" statement* "}"
        | "if" "(" expr ")" "{" statement* "}" "else" "{" statement* "}"
        | "if" "(" expr ")" "{" statement* "}"
        | "return" expr ";"
        | "return" ";";

    expr:
        ADD_OPER expr | unary;
    unary:
        additive COMP_OPER unary | additive;
    additive:
        multitive ADD_OPER additive | multitive;
    multitive:
        call MULT_OPER multitive | call;

    call:
        fndef "(" csexpr ")" | fndef "(" ")" | fndef;
    csexpr:
        expr "," csexpr | expr;

    fndef:
          "function" VARIABLE "(" csvar ")" "{" statement* "}"
        | "function" VARIABLE "(" ")" "{" statement* "}"
        | primary;
    csvar:
        VARIABLE "," csvar | VARIABLE;

    primary:
          "(" expr ")"
        | atom;
    atom:
          NUMBER
        | STRING
        | VARIABLE;
