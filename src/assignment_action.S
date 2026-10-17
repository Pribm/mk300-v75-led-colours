.text
.global assignment_hold_store
assignment_hold_store:
    r1 = r6 * 6
    r1 += r13
    r1 = r1 + 0x12d
    b[r1] = r0
    goto assignment_continuation
.org 0x2a
.global assignment_click_store
assignment_click_store:
    r1 = r6 * 6
    r1 += r13
    r1 = r1 + 0x12c
    b[r1] = r0
    call full_policy
assignment_continuation:
