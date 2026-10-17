#include <stdint.h>
uint32_t hold_hue_opposite(uint32_t c) {
    uint32_t r=(c>>16)&255u, g=(c>>8)&255u, b=c&255u;
    uint32_t s;
    if (r>=g) {
        if (r>=b) {
            if (g>=b) { s=r+b; return (b<<16)|((s-g)<<8)|r; }
            s=r+g; return (g<<16)|(r<<8)|(s-b);
        }
        s=b+g; return ((s-r)<<16)|(b<<8)|g;
    }
    if (g>=b) {
        if (b>=r) { s=g+r; return (g<<16)|(r<<8)|(s-b); }
        s=g+b; return ((s-r)<<16)|(b<<8)|g;
    }
    s=b+r; return (b<<16)|((s-g)<<8)|r;
}
