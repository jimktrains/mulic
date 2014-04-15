#!/usr/bin/env python3

from copy import deepcopy
import sys

def parse(prog):
    prog = prog.replace('(', ' ( ').replace(')', ' ) ').split()
    return parse_helper(prog);

def parse_helper(prog):
    stack = []
    while(len(prog) > 0):
        tok = prog.pop(0)
        if tok == '(':
            stack.append(parse_helper(prog))
        elif tok == ')':
            return tuple(stack)
        else:
            stack.append(tok)
    return stack


last_reg =lambda x : x[-1][1]

next_jump = 0
def get_next_jump():
    global next_jump
    next_jump += 1
    return "trgt%d" % next_jump
all_instr = lambda x : "\n".join([i[0] for i in x])

class Add:
    @staticmethod
    def run(env, args):
        x = args[0]
        y = args[1]
        x = x[0] + y[0]
        return [x]
    @staticmethod
    def compile(env, args):
        x = args[0]
        y = args[1]
        x = x + y + [("ADD %s, %s" % (last_reg(x),last_reg(y)), last_reg(x))]
        return x
class In:
    @staticmethod
    def run(env, x):
        x=int(input("%s> " % x[0][0]))
        return [x]
    @staticmethod
    def compile(env, x):
        reg = get_reg()
        return [("IN %s, %s" % (reg, x[0][0]), reg)]
class Out:
    @staticmethod
    def run(env, args):
        x = args[0]
        y = args[1]
        print("%s:\t%d"% (x[0], y[0]))
        return [(None, None)]
    @staticmethod
    def compile(env, args):
        return [("OUT %s, %s" % (x[0][0],last_reg(y)),last_reg(y))]

class If:
    args = 3
    def run(env, args):
        ex = args[0]
        t = args[1]
        f = args[3]

        ex = run(ex, evn)
        if ex[0] == 1:
            x = run(t, env)
            return [x]
        else:
            x = run(f, env)
            return [x]
    def compile(ex, t, f):
        tgt = get_next_jump();
        tend = get_next_jump();

        t = compile(t, env)
        f = compile(f, env)
        ex = compile(ex, env)

        s = all_instr(ex) + "\n"
        s += "SUBI %s,1\n" % last_reg(ex)
        s += "BRNE %s\n" % tgt
        s += all_instr(t) + "\n"
        s += "JMP %s\n" % tend
        s += "%s:\n" % tgt
        s += all_instr(f) + "\n"
        s += "%s:\n" % tend

        return [(s, None)]

class Load:
    def run(x): return [x]
    def compile(x):
        reg = get_reg()
        return [("LDI %s, %d" % (reg, x), reg)]
        
primatives = {
    "add": Add,
    "in":  In,
    "out": Out,
}

macros = {
    "if": If
}

def walk_program(prog, execfn, env):
    if type(prog) is list:
        accum = []
        for subprog in prog:
            accum.append(walk_program(subprog, execfn, env))
        return accum
    elif type(prog) is tuple:
       cmd = walk_program(prog[0], execfn, env)
       if cmd in env['procs']:
            cmd = env['procs'][cmd]
            args = []
            for i in range(1,len(prog)):
                args.append(walk_program(prog[i], execfn, env))
            return getattr(cmd, execfn)(env, args)
       elif cmd in env['macros']:
            cmd = env['macros'][cmd]
            args = []
            for i in range(1,len(prog)):
                args.append(walk_program(prog[i], execfn, env))
            return getattr(cmd, execfn)(env, args)
    else:
        if prog.isdigit():
            return int(prog)
        return prog

reg_free = [ "r%d" % i for i in range(32) ]
reg_used = []

def get_reg():
    if len(reg_free) < 1:
        raise "No more registers!"
    x = reg_free.pop()
    reg_used.append(x)
    return x

def free_reg(reg):
    x = reg_free.append(reg)
    reg_used.remove(reg)

def run(prog, env = None):
    if env is None:
        env = {
            "procs": primatives,
            "macros": macros,
        }
    return walk_program(prog, 'run', env)
def compile(prog, env = None):
    if env is None:
        env = {
            "procs": primatives,
            "macros": macros,
        }
    return walk_program(prog, 'compile', env)

prog = "(out PORTC (add (in PORTB) (add 2 2)))"
prog = """
(if (in PORTF) ((out PORTC (add (add 1 2) (in PORTB)))
                (out PORTC 55))
               (out PORTA (add (add 2 2) (in PORTC))))
(out PORTD 42)
"""
print(prog)
prog = parse(prog)
print(prog)

run(deepcopy(prog))
print(all_instr(compile(deepcopy(prog))))
