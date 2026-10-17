.text
.global active_sync_guard
active_sync_guard:
    r0 = 0x1844a454
    if (r4 != r0) goto .Lreturn
    goto module_only_sync
.Lreturn:
    rts
