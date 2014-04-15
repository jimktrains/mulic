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


last_reg =lambda x : x[-1][1]

class Add:
    args = 2
    def run(x, y):
        x = x[0] + y[0]
        return [x]
    def compile(x, y):
        x = x + y + [("ADD %s, %s" % (last_reg(x),last_reg(y)), last_reg(x))]
        return x
class In:
    args = 1
    def run(x):
        x=int(input("%s> " % x[0]))
        return [x]
    def compile(x):
        reg = get_reg()
        return [("IN %s, %s" % (reg, x[0]), reg)]
class Out:
    args = 2
    def run(x, y):
        print("%s:\t%d"% (x[0], y[0]))
    def compile(x, y):
        return [("OUT %s, %s" % (x[0],last_reg(y)),last_reg(y))]


next_jump = 0
def get_next_jump():
    global next_jump
    next_jump += 1
    return "trgt%d" % next_jump
all_instr = lambda x : "\n".join([i[0] for i in x])

class If:
    args = 3
    def run(ex, t, f):
        ex = run(ex)
        if ex[0] == 1:
            x = run(t)
            return [x]
        else:
            x = run(f)
            return [x]
    def compile(ex, t, f):
        tgt = get_next_jump();
        tend = get_next_jump();

        t = compile(t, False)
        f = compile(f, False)
        ex = compile(ex, False)

        s = all_instr(ex) + "\n"
        s += "SUBI %s,1\n" % last_reg(ex)
        s += "BRNE %s\n" % tgt
        s += all_instr(t) + "\n"
        s += "JMP %s\n" % tend
        s += "%s:\n" % tgt
        s += all_instr(f) + "\n"
        s += "%s:\n" % tend

        return (s, None)

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

def walk_program(prog, execfn, env, printit):
    if type(prog) is list:
        r = walk_program(prog[0], execfn, env, printit)
        if type(r[0]) is not list:
            ret = [(None,None)]
            if r[0] in env['procs']:
                cmd = env['procs'][r[0]]
                if cmd.args == 0:
                    ret = getattr(cmd, execfn)()
                elif cmd.args == 1:
                    ret = getattr(cmd, execfn)(
                        walk_program(prog[1], execfn, env, printit)
                    )
                elif cmd.args == 2:
                    ret = getattr(cmd, execfn)(
                        walk_program(prog[1], execfn, env, printit),
                        walk_program(prog[2], execfn, env, printit)
                    )
                elif cmd.args == 3:
                    ret = getattr(cmd, execfn)(
                        walk_program(prog[1], execfn, env, printit),
                        walk_program(prog[2], execfn, env, printit),
                        walk_program(prog[3], execfn, env, printit)
                    )
            elif r[0] in env['macros']:
                cmd = env['macros'][r[0]]
                if cmd.args == 0:
                    ret = getattr(cmd, execfn)()
                elif cmd.args == 1:
                    ret = getattr(cmd, execfn)(
                        prog[1]
                    )
                elif cmd.args == 2:
                    ret = getattr(cmd, execfn)(
                        prog[1],
                        prog[2],
                    )
                elif cmd.args == 3:
                    ret = getattr(cmd, execfn)(
                        prog[1],
                        prog[2],
                        prog[3],
                    )
            else:
                print(r)
                return r
            return ret
        if len(prog) > 1:
            prog.pop(0)
            return walk_program(prog, execfn, env, printit)
        return r
    else:
        if prog.isdigit():
            ld = getattr(Load, execfn)(int(prog))
            return ld
        else:
            return [prog]
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

def run(prog, printit = True):
    env = {
        "procs": primatives,
        "macros": macros,
    }
    return walk_program(prog, 'run', env, printit)
def compile(prog, printit = True):
    env = {
        "procs": primatives,
        "macros": macros,
    }
    return walk_program(prog, 'compile', env, printit)

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
