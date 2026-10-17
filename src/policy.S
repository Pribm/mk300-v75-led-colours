.text
/* Stateless combined Click/Hold policy. Preserve the proven r12 frame.
 * Tags: 0=Click only, 0xfd=dual, 0xfe=Hold only. */
.global module_ctl_policy
.type module_ctl_policy,@function
module_ctl_policy:
    [--sp] = {rets, r12-r4}
    r4 = 0
    goto .Linit
.global module_ctl_sync
.type module_ctl_sync,@function
module_ctl_sync:
    [--sp] = {rets, r12-r4}
    r4 = 1
.Linit:
    r9 = 0
    r6 = 0x1844a59e
    r8 = r6 + -0x14a
.Lloop:
    call .Lfar_enter
    r7 = b[r6+0] (u)
    r1 = b[r6+1] (u)
    if (r7 != 0) goto .Lnot_click
    if (r1 != 0) goto .Lpolicy
    r7 = 0xfd
    goto .Lpolicy
.Lnot_click:
    if (r1 == 0) goto .Lhold_ctl
    if (r4 != 0) goto .Lafter_group
    goto .Lpolicy
.Lhold_ctl:
    r7 = 0xfe
.Lpolicy:
    r11 = [r8+0x14]
    if (r7 == 0) goto .Lmodule
    if (r7 == 0xfe) goto .Lmodule
    if (r7 == 0xfd) goto .Lmodule
    if (r7 == 1) goto .Lfixed
    if (r7 == 2) goto .Lselected
    if (r7 == 4) goto .Lconditional
    if (r7 == 20) goto .Ldisabled
.Llit:
    r0 = r11
.Loutput:
    r1 = r9
    call .Lfar_group
.Lafter_group:
    call policy_critical_exit
    if (r4 != 0) goto .Lnext
    if (r9 < 2) goto .Lnext
    /* Preserve the existing LCD arguments; combined hues are LEDs only.
     * Original policy made its LCD colour zero for raw-empty/disabled masks. */
    r2 = r11
    r1 = b[r6+0] (u)
    if (r1 == 0) goto .Llcd_click_mask
    r0 = b[r6+1] (u)
    if (r0 != 0) goto .Llcd_call
    r0 = h[r6+4] (u)
    goto .Llcd_mask
.Llcd_click_mask:
    r0 = h[r6+2] (u)
.Llcd_mask:
    if (r0 == 0) goto .Llcd_zero
    if ((r0 & 0x800) == 0) goto .Llcd_call
.Llcd_zero:
    r2 = 0
.Llcd_call:
    r0 = r9 + -2
    call .Lfar_lcd
.Lnext:
    r6 += 6
    r9 += 1
    if (r9 != 4) goto .Lloop
    {pc, r12-r4} = [sp++]
.Lmodule:
    if (r7 == 0xfd) goto .Ldual
    if (r7 == 0xfe) goto .Lsingle_hold
    r1 = h[r6+2] (u)
    call selected_any_on
    if (r0 != 0) goto .Llit
    goto .Loff
.Lsingle_hold:
    r1 = h[r6+4] (u)
    call selected_any_on
    if (r1 == 0) goto .Loff
    if (r0 != 0) goto .Llit
    goto .Lhue180
.Ldual:
    r1 = h[r6+2] (u)
    call selected_any_on
    r7 = r0
    r1 = h[r6+4] (u)
    call selected_any_on
    if (r0 != 0) goto .Lhold_on
    if (r7 != 0) goto .Llit
.Loff:
    r0 = 0
    goto .Loutput
.Lhold_on:
    if (r7 == 0) goto .Lhue180
    r0 = r11
    call hue_quarter_turn
    goto .Loutput
.Lhue180:
    r0 = r11
    call hue_opposite
    goto .Loutput
.Ldisabled:
    r11 = 0
    goto .Llit
.Lfixed:
    r11 = 0x872657
    goto .Llit
.Lselected:
    call .Lfar_select
    r1 = 0x180fabbc
    r11 = [r1+r0<<2]
    goto .Llit
.Lconditional:
    r1 = r8 + -0x1b60
    r1 = b[r1+0] (u)
    if (r1 != 0) goto .Llit
    r0 = 0
    goto .Loutput
.size module_ctl_policy, .-module_ctl_policy

/* r1=raw unsigned16 mask; returns r0=any enabled byte, r1=effective
 * low11 mask. r2/r3 are scratch. r8 remains the active preset pointer. */
.global selected_any_on
.type selected_any_on,@function
selected_any_on:
    r0 = 0
    if ((r1 & 0x800) != 0) goto .Lmask_disabled
    r1 <<= 21
    r1 >>= 21
    if (r1 == 0) goto .Lmask_return
    r2 = r1
    r3 = r8 + 0x2b
.Lmask_scan:
    if ((r2 & 1) == 0) goto .Lmask_advance
    r0 = b[r3+0] (u)
    if (r0 != 0) goto .Lmask_return
.Lmask_advance:
    r3 += 1
    r2 >>= 1
    if (r2 != 0) goto .Lmask_scan
.Lmask_return:
    rts
.Lmask_disabled:
    r1 = 0
    rts
.size selected_any_on, .-selected_any_on

.global policy_critical_exit
policy_critical_exit:
    csync
    r0 = [r5]
    r0 += -1
    [r5] = r0
    if (r0 != 0) goto .Lunlocked
    lockclr
.Lunlocked:
    icfg = r10
    rts

.Lfar_veneer_start:
.Lfar_enter:
    r12 = 0x1808555e
    goto r12
.Lfar_group:
    r12 = 0x1802eaee
    goto r12
.Lfar_lcd:
    r12 = 0x1803476c
    goto r12
.Lfar_select:
    r12 = 0x1803487c
    goto r12
