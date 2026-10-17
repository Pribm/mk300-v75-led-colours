.text
.global post_update_wrapper
.set local_unlock, post_update_wrapper-0x10
post_update_wrapper:
    [--sp] = {rets, r5-r4}
    r5_r4 = r1_r0
    call original_prepare
    r1_r0 = r5_r4
    call original_apply
    call active_sync_guard
    call local_unlock
    {pc, r5-r4} = [sp++]
