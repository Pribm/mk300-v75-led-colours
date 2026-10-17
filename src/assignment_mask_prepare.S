.text
.global assignment_mask_prepare
assignment_mask_prepare:
    r9 = r3 | (1 << r7)
    r4 = r2 + 0x14c
    r2 = r1 << 1
    r2 += r4
    r2 = h[r2] (u)
