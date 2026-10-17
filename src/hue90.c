#include <stdint.h>

/* Exact hue +90 in doubled chroma units. No division by chroma, floating
 * point, lookup table, runtime data, or external call is required. */
uint32_t hue_quarter_turn(uint32_t rgb) {
    int r = (rgb >> 16) & 255, g = (rgb >> 8) & 255, b = rgb & 255;
    /* A volatile local retains explicit conditional stores: the available
     * corrected Ghidra processor does not decode compiler umax/smax forms.
     * Freeze the result immediately; the stack word never escapes. */
    volatile int maximum = r;
    if (g >= maximum) maximum = g;
    if (b >= maximum) maximum = b;
    int hi = maximum;
    int lo = r < g ? r : g;
    if (b < lo) lo = b;
    int d = hi - lo;
    if (!d) return rgb & 0xffffff;
    int d2 = d + d, d4 = d2 + d2, d6 = d4 + d2, d12 = d6 + d6;
    int h2;
    if (hi == r) {
        h2 = 2 * (g - b);
        if (h2 < 0) h2 += d12;
    } else if (hi == g) {
        h2 = 2 * (b - r) + d4;
    } else {
        h2 = 2 * (r - g) + d4 + d4;
    }
    h2 += d2 + d;  /* Add 1.5 hue sextants. */
    if (h2 >= d12) h2 -= d12;
    if (h2 < d2) {
        r = hi; g = lo + ((h2 + 1) >> 1); b = lo;
    } else if (h2 < d4) {
        r = lo + ((d4 - h2 + 1) >> 1); g = hi; b = lo;
    } else if (h2 < d6) {
        r = lo; g = hi; b = lo + ((h2 - d4 + 1) >> 1);
    } else if (h2 < d4 + d4) {
        r = lo; g = lo + ((d4 + d4 - h2 + 1) >> 1); b = hi;
    } else if (h2 < d6 + d4) {
        r = lo + ((h2 - d4 - d4 + 1) >> 1); g = lo; b = hi;
    } else {
        r = hi; g = lo; b = lo + ((d12 - h2 + 1) >> 1);
    }
    return ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
}
