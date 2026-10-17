.section .routes,"ax",@progbits
.global module_ctl_policy_route
.type module_ctl_policy_route,@function
module_ctl_policy_route:
    goto .Lpolicy_far
.space 4
.global module_ctl_sync_route
.type module_ctl_sync_route,@function
module_ctl_sync_route:
    goto .Lsync_far
.space 14
.Lpolicy_far:
    r0 = 0x1804726e
    goto r0
.Lsync_far:
    r0 = 0x18047274
    goto r0
.space 136
.global policy_critical_exit_route
.type policy_critical_exit_route,@function
policy_critical_exit_route:
    r0 = policy_critical_exit
    goto r0
.space 14
