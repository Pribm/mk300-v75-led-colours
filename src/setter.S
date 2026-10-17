.text
.global setter
setter:
    [--sp] = {rets, r6-r4}
    r5_r4 = r1_r0
    r0 = 0
    if (r4 == 0) goto .Lreturn
    if (r5 > 10) goto .Lreturn
    r6 = 1
    if (r2 != 0) goto .Lnormalized
    r6 = r2
.Lnormalized:
    if (r5 != 3) goto .Lnormal
    if (r6 == 0) goto .Lnormal
    r0 = r4
    call module3_check
    if (r0 == 0) goto .Lnormal
    r0 = 0
    b[r4+46] = r0
    r1 = 0x18447f27
    r2 = 1
    b[r1] = r2
    goto .Lsync
.Lnormal:
    r0 = r4 + r5
    b[r0+43] = r6
    r0 = 1
.Lsync:
    // Custom helper input: active preset candidate pointer is in r4.
    // r6 is callee saved, so the normal ABI preserves the setter result.
    r6 = r0
    call setter_sync
    r0 = r6
.Lreturn:
    {pc, r6-r4} = [sp++]
