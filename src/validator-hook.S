/* Guarded fixed-size validator hook. No original data/code outside listed spans changes. */
.text
.global validator_patch_start,validator_guard,validator_zero_byte,validator_zero_pair,validator_loop_test
validator_patch_start:
    /* Entry facts from preceding assignment loop: r1=20,r2=r8+24,r3=0.
     * Populate the same seven stack pointers in the same order, using a loop. */
    r4 = r8 + 0x18
    r0 = r4
    r1 = sp + 8
    r2 = 7
.Lpointers:
    [r1++=4] = r0
    r0 += 8
    if (--r2 != 0) goto .Lpointers
    r0 += -8
    r1 = 20
    r2 = r8 + 0x18
    r5 = 1
    r8 = r5
    r10 = 11
    r11 = 0
    goto validator_item
validator_guard:
    r6 = r0
    r0 = 0x1844a454
    if (r9 != r0) goto validator_restore
    call full_policy
    goto validator_restore
    .incbin "validator-original-window.bin", 56, 52
    goto validator_loop_test
    .incbin "validator-original-window.bin", 110, 18
    goto validator_zero_pair
    .incbin "validator-original-window.bin", 130, 128
    if (r6 == 0) goto validator_zero_pair
    if (r12 == 0) goto validator_zero_pair
    .incbin "validator-original-window.bin", 264, 34
validator_zero_byte:
    b[r4+2] = r1
validator_zero_pair:
    r1 = 0
    h[r4+6] = r1
    h[r4+4] = r1
validator_loop_test:
    if (r5 != 7) goto validator_next
    goto validator_guard
validator_restore:
    r0 = r6
validator_return:
    sp += 0x40
    {pc, r14-r4} = [sp++]
.set validator_next, validator_patch_start + 0x38
.set validator_item, validator_patch_start + 0x6e
