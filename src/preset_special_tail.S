.text
.global special_tail
special_tail:
    r0 = r7 + 0x1db
    r1 = r10 + 0x10eb
    r2 = b[r0+1] (u)
    r3 = b[r0] (u)
    b[r1+1] = r2
    b[r1] = r3
    call module_sync
    r0 = 0x10eb
    nop
    nop
    nop
    nop
