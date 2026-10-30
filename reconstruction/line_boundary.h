#ifndef NFS3_LINE_BOUNDARY_H
#define NFS3_LINE_BOUNDARY_H

/* Original storage: binary32 pair at 00791c08/00791c0c. Shared, not reentrant. */
extern float gLineBoundaryCandidate_00791c08[2];

/* Test C ABI, not the game's EAX/EDX/EBX/ECX + RET4 ABI.
 * Arrays: candidate[2], sourceLine[4], bounds[yMin,xMin,yMax,xMax].
 * Returns shared scratch or null; writes may occur even on rejection.
 * Initial supported test domain: aligned, nonaliasing valid buffers; x87 CW037f.
 */
float *Nfs3LineBoundaryCandidate_00485c30(
    const float *candidate, const float *sourceLine, const float *bounds,
    unsigned int returnPolicy, unsigned char *edgeMask);
#endif
