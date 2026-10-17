.text
.global normal_early_sync
normal_early_sync:
    if (r0 == 0) goto normal_sync_site
.org 0x16
.global normal_loop_index
normal_loop_index:
    r0 = r7 + r11
.org 0x16e
.global normal_loop_tail
normal_loop_tail:
    r7 += 1
    r14 = r14 + 6
    r15 = r15 + 8
    if (r15 != 16) goto normal_loop_index
normal_sync_site:
    call module_sync
