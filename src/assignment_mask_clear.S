.text
.global assignment_mask_clear
assignment_mask_clear:
    r0 = b[r8+7] (u)
    r1 = r0 << 1
    r2 = r4 + r1
    r1 = h[r2] (u)
    r1 = r1 & ~r9
    h[r2] = r1
    if (r0 != 0) goto .Ldone
    r11_r10 = r1_r0
    call full_policy
    r1_r0 = r11_r10
.Ldone:
    nop
    nop
    nop
    nop
    nop
