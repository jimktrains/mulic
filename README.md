mulic
=====

LISP compiler for AVR microprocessors

Right now, given the program:

    (out PORTC (add (in PORTB) (add 2 2)))

When being run, it'll ask for input:

    PORTB> 5

And then produce the output:

    PORTC:9

When being compiled, it'll produce:

    IN r31, PORT    B
    LDI r30, 2
    LDI r29, 2
    ADD r30, r29
    ADD r31, r30
    OUT PORTC, r31

I still need to get macros (think delayed execution as in an if statement) working, as right now I assume each branch will execute. I also need list support (it is LISP afterall). Also, I need to be able to define lambdas and byte arrays.  It's a work in progress.
