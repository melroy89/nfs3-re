#include "line_boundary.h"

/* Address trace: 00485c30..00485f1a; preserved original, not canonical clipping.
 * Volatile stores model FST/FSTP binary32 boundaries. long double models live
 * x87 intermediates under the selected i686 compiler/flags, not Windows source
 * type recovery. No alias/reentrancy or complete floating-status claim.
 */
_Static_assert(__CHAR_BIT__ == 8, "8-bit bytes required");
_Static_assert(sizeof(float) == 4 && __FLT_MANT_DIG__ == 24 && __FLT_MAX_EXP__ == 128,
               "IEEE binary32 storage required");
_Static_assert(__LDBL_MANT_DIG__ == 64 && __LDBL_MAX_EXP__ == 16384,
               "x87 extended long double required for this implementation");
_Static_assert(sizeof(unsigned int) == 4, "32-bit policy/bit representation required");
float gLineBoundaryCandidate_00791c08[2];

static unsigned int bits(float value)
{
    unsigned int result;
    __builtin_memcpy(&result, &value, sizeof result);
    return result;
}

static void store_component(unsigned int index, long double value)
{
    *(volatile float *)&gLineBoundaryCandidate_00791c08[index] = (float)value;
}

/* 00485cc7/00485d15/00485d8e/00485ddb and central counterparts:
 * lower-x test consumes the extended FST-retained value; upper-x test reloads
 * binary32 scratch. JC rejects unordered at the first test; JA does not at the
 * second. Do not combine these as an ordinary closed-interval predicate.
 */
static int intersect_y(float y, float slope, float intercept,
                       const float *bounds, unsigned char *mask,
                       unsigned char side, int y_already_written)
{
    long double x = ((long double)y - (long double)intercept) / (long double)slope;
    store_component(0, x);
    if (!(x >= (long double)bounds[1]))
        return 0;
    if ((long double)*(volatile float *)&gLineBoundaryCandidate_00791c08[0] >
        (long double)bounds[3])
        return 0;
    if (!y_already_written)
        store_component(1, (long double)y);
    *mask = (unsigned char)(*mask | side);
    return 1;
}

float *Nfs3LineBoundaryCandidate_00485c30(
    const float *candidate, const float *sourceLine, const float *bounds,
    unsigned int returnPolicy, unsigned char *edgeMask)
{
    /* 00485c40..00485c6f: four explicit binary32 difference stores. */
    volatile float left = (float)((long double)candidate[0] - (long double)bounds[1]);
    volatile float right = (float)((long double)bounds[3] - (long double)candidate[0]);
    volatile float dx = (float)((long double)sourceLine[0] - (long double)sourceLine[2]);
    volatile float below = (float)((long double)candidate[1] - (long double)bounds[0]);
    volatile float slope;
    volatile float intercept;
    int accepted = 1;

    if ((bits(dx) & 0x7fffffffU) == 0)
        slope = 0.0f; /* 00485c88: both signed-zero deltas select positive zero. */
    else
        slope = (float)(((long double)sourceLine[1] - (long double)sourceLine[3]) /
                        (long double)dx);
    intercept = (float)((long double)sourceLine[3] -
                        (long double)slope * (long double)sourceLine[2]);

    /* 00485ca3/00485d6a: JBE on (0 compared with stored difference).
     * Unordered takes the same branch as <=, hence these positive tests.
     */
    if (0.0L > (long double)left || 0.0L > (long double)right) {
        const int at_left = 0.0L > (long double)left;
        const float x = at_left ? bounds[1] : bounds[3];
        const unsigned char side = at_left ? 4 : 8;
        long double y = (long double)slope * (long double)x + (long double)intercept;
        store_component(1, y);
        /* 00485cbd/00485d84: JNC excludes unordered from >=. */
        if (!(y >= (long double)bounds[0])) {
            accepted = intersect_y(bounds[0], slope, intercept, bounds, edgeMask, 1, 0);
        } else if ((long double)*(volatile float *)&gLineBoundaryCandidate_00791c08[1] >
                   (long double)bounds[2]) {
            accepted = intersect_y(bounds[2], slope, intercept, bounds, edgeMask, 2, 0);
        } else {
            store_component(0, (long double)x);
            *edgeMask = (unsigned char)(*edgeMask | side);
        }
    } else {
        /* 00485e30: unordered follows upper-Y branch, not lower-Y branch. */
        const int lower = 0.0L > (long double)below;
        const float y = lower ? bounds[0] : bounds[2];
        const unsigned char side = lower ? 1 : 2;
        if ((bits(slope) & 0x7fffffffU) == 0) {
            /* 00485e3f/00485ea7: no division; sourceLine[0] then boundary. */
            const long double x = (long double)sourceLine[0];
            store_component(1, (long double)y);
            store_component(0, x);
            *edgeMask = (unsigned char)(*edgeMask | side);
        } else {
            /* 00485e65/00485ecd writes Y before storing/testing candidate X. */
            store_component(1, (long double)y);
            accepted = intersect_y(y, slope, intercept, bounds, edgeMask, side, 1);
        }
    }
    return accepted || returnPolicy == 0 ? gLineBoundaryCandidate_00791c08 : (float *)0;
}
