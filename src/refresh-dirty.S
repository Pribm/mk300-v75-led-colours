.text
.global ledc_refresh_dirty_safe
.type ledc_refresh_dirty_safe,@function
ledc_refresh_dirty_safe:
    .incbin "original-timer.bin", 0, 0x2a
.Lreturn:
    .incbin "original-timer.bin", 0x2a, 0x10
    // Every nonzero original count selects exactly 12 pixels.
    // r8 is saved/restored and no longer needed as an intermediate constant.
    if (r0 == 0) goto .Lreturn
    .incbin "original-timer.bin", 0x44, 0x16
    r4 = 36
    // Original lane loop remains byte-exact; internal relative branches move together.
    .incbin "original-timer.bin", 0x60, 0x3a
    if (r11 == 0) goto .Lafter_dirty
    r0 = r11
    b[r13+0x38] = r0
.Lafter_dirty:
    if ((r14 & 0xff) == 0) goto .Lreturn
    .incbin "original-timer.bin", 0xa4, 8
    r0 = 288
    .incbin "original-timer.bin", 0xb4, 10
.Ltimer_end:
.size ledc_refresh_dirty_safe, .Ltimer_end-ledc_refresh_dirty_safe
// This leaf has no relative operands. Preserve its complete stock body and ABI.
.global relocated_fatal_flag
relocated_fatal_flag:
    .incbin "original-flag.bin"
.global original_fatal_flag_entry
original_fatal_flag_entry:
    goto relocated_fatal_flag
