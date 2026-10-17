.text
.global post_update_direct
.set no_update, post_update_direct + 0x1e4
.set continuation, post_update_direct + 0x2c
post_update_direct:
    r0 = r11 + 0x200
    r0 = b[r0] (u)
    if (r0 == 0) goto no_update
    r2 = b[r11+0x32] (u)
    call original_select
    r1 = 1
    if (r2 == r0) goto continuation
    r0 = r11 + r7
    r1 = 0
    call original_apply
    call module_only_sync
    r1 = r11 + 0x200
    r1 = b[r1] (u)
