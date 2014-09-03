#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from js.main import main


def target(driver, args):
    return main, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()
