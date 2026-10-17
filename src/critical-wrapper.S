.text
/* Private pair: r5=per-core global-lock counter address; r10=saved ICFG.
 * Callers must preserve both across the protected region and save them for ABI.
 * The exact SDK local_irq_save/restore sequence preserves every incoming ICFG bit.
 */
.global original_read_wrapper
original_read_wrapper:
    [--sp] = {rets, r11-r4}
    call policy_critical_enter
    r1 = 0x00ff0508
    r1 = [r1]
    /* Stock wrapper leaves IRQ enabled iff its incoming IRQ nesting was zero.
     * Keep that legacy behavior here; ordinary policy exits restore exact ICFG.
     */
    r0 = [r5+8]
    r10 = r10 & ~0x100
    if (r0 != 0) goto .Lwrapper_leave
    r10 = r10 | 0x100
.Lwrapper_leave:
    call policy_critical_exit
    {pc, r11-r4} = [sp++]
.global policy_critical_enter
policy_critical_enter:
    r10 = icfg
    r0 = r10 & ~0x100
    icfg = r0
    r5 = 0x00103e94
    r0 = cnum
    r0 <<= 2
    r5 += r0
    r0 = [r5]
    r1 = r0 + 1
    [r5] = r1
    if (r0 != 0) goto .Lentered
    lockset
.Lentered:
    csync
    rts
