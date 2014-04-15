#!/usr/bin/env python3

from copy import deepcopy

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
            return stack
        else:
            stack.append(tok)
    return stack

class Add:
    def run(x, y):
        x = x + y
        return x
    def compile(x, y):
        free_reg(y)
        return ("ADD %s, %s" % (x,y), x)
class Sub:
    def run(x, y):
        x = x - y
        return x
    def compile(x, y):
        free_reg(y)
        return ("SUB %s, %s" % (x,y), x)
class In:
    def run(x):
        return int(input("%s> " % x))
    def compile(x):
        reg = get_reg()
        return ("IN %s, %s" % (reg, x), reg)
class Out:
    def run(x, y):
        print("%s:\t%d"% (x, y))
    def compile(x, y):
        return ("OUT %s, %s" % (x,y),y)

primatives = {
    "add": (2, Add),
    "sub": (2, Sub),
    "in": (1, In),
    "out": (2, Out),
}

def run(prog):
    if type(prog) is list:
        r = run(prog[0])
        if r in primatives:
            cmd = primatives[r]
            if cmd[0] == 0:
                return cmd[1].run()
            elif cmd[0] == 1:
                return cmd[1].run(run(prog[1]))
            elif cmd[0] == 2:
                return cmd[1].run(run(prog[1]), run(prog[2]))
        return r
    else:
        if prog.isdigit():
            return int(prog)
        else:
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

def compile(prog):
    if type(prog) is list:
        r = compile(prog[0])
        if r in primatives:
            cmd = primatives[r]
            if cmd[0] == 0:
                r = cmd[1].compile()
                print(r[0])
                return r[1]
            elif cmd[0] == 1:
                r = cmd[1].compile(compile(prog[1]))
                print(r[0])
                return r[1]
            elif cmd[0] == 2:
                r = cmd[1].compile(compile(prog[1]), compile(prog[2]))
                print(r[0])
                return r[1]
        return r
    else:
        # Just assume that non numbers are proc names
        if prog.isdigit():
            reg = get_reg()
            print("LDI %s, %d" % (reg, int(prog)))
            return reg
        else:
            return prog

prog = "(out PORTC (add (in PORTB) (add 2 2)))"
print(prog)
prog = parse(prog)
print(prog)

run(deepcopy(prog))
compile(deepcopy(prog))
