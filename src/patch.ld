SECTIONS
{
    . = 0x180348ba;
    .routes : { *(.routes) }
    . = 0x1804726e;
    .extension : { *(.text) *(.text.*) }
    ASSERT(. <= 0x18047606, "extension exceeds disabled APU handler")
}
