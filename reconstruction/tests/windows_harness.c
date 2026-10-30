#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../line_boundary.h"

typedef struct {
    float point[2], line[4], bounds[4];
    uint32_t policy, initial_mask, control_word;
} Input;
typedef struct {
    uint32_t returned, c0, c1, mask;
    uint16_t cw, sw;
    uint32_t raw_return;
} Result;
extern void nfs3_call_original(void *, float *, float *, float *, uint32_t,
                               uint8_t *, void *, Result *);

static void set_fpu(uint16_t cw) {
    __asm__ volatile("fninit\n\tfldcw %0" : : "m"(cw));
}
static void record_c(Result *r, float *ret, uint8_t *mask) {
    uint32_t a, b;
    memcpy(&a, &gLineBoundaryCandidate_00791c08[0], 4);
    memcpy(&b, &gLineBoundaryCandidate_00791c08[1], 4);
    r->returned = (uint32_t)(uintptr_t)ret;
    r->raw_return = r->returned;
    r->c0 = a; r->c1 = b; r->mask = *mask;
    __asm__ volatile("fnstcw %0" : "=m"(r->cw));
    __asm__ volatile("fnstsw %0" : "=m"(r->sw));
}

int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: harness function.bin vectors.bin output.bin\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    unsigned char code[747];
    if (fread(code, 1, sizeof code, f) != sizeof code || fgetc(f) != EOF) return 2;
    fclose(f);
    f = fopen(argv[2], "rb");
    if (!f) { perror(argv[2]); return 2; }
    struct { uint32_t before[4]; Input inputs[40]; uint32_t after[4]; } guarded;
    memset(&guarded, 0xA5, sizeof guarded);
    if (fread(guarded.inputs, sizeof(Input), 40, f) != 40 || fgetc(f) != EOF) return 2;
    unsigned char input_snapshot[sizeof guarded.inputs];
    memcpy(input_snapshot, guarded.inputs, sizeof input_snapshot);
    fclose(f);

    void *code_map = VirtualAlloc(NULL, 0x10000,
                                  MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    void *scratch = VirtualAlloc(NULL, 0x10000,
                                 MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    if (!code_map || !scratch || (uintptr_t)code_map > UINT32_MAX ||
        (uintptr_t)scratch > UINT32_MAX) {
        fprintf(stderr, "private VirtualAlloc failed: code=%p scratch=%p error=%lu\n",
                code_map, scratch, (unsigned long)GetLastError());
        return 3;
    }
    static const struct { uint16_t offset; uint32_t original; } scratch_operands[29] = {
        {0x099,0x00791c08},{0x0a7,0x00791c08},{0x0e7,0x00791c08},
        {0x0f5,0x00791c08},{0x127,0x00791c08},{0x160,0x00791c08},
        {0x16e,0x00791c08},{0x1ad,0x00791c08},{0x1bb,0x00791c08},
        {0x1ed,0x00791c08},{0x220,0x00791c08},{0x23c,0x00791c08},
        {0x24a,0x00791c08},{0x289,0x00791c08},{0x2a4,0x00791c08},
        {0x2b2,0x00791c08},{0x2db,0x00791c08},
        {0x084,0x00791c0c},{0x0bc,0x00791c0c},{0x0d0,0x00791c0c},
        {0x10b,0x00791c0c},{0x14b,0x00791c0c},{0x182,0x00791c0c},
        {0x196,0x00791c0c},{0x1d1,0x00791c0c},{0x217,0x00791c0c},
        {0x236,0x00791c0c},{0x280,0x00791c0c},{0x29e,0x00791c0c}
    };
    for (unsigned int i = 0; i < 29; ++i) {
        uint32_t value;
        memcpy(&value, code + scratch_operands[i].offset, sizeof value);
        if (value != scratch_operands[i].original) {
            fprintf(stderr, "scratch relocation byte witness changed at +0x%x\n",
                    scratch_operands[i].offset); return 4;
        }
    }
    unsigned char private_code[sizeof code];
    memcpy(private_code, code, sizeof private_code);
    for (unsigned int i = 0; i < 29; ++i) {
        uint32_t relocated = (uint32_t)(uintptr_t)scratch + 0x1c08 +
                             (scratch_operands[i].original - 0x00791c08);
        memcpy(private_code + scratch_operands[i].offset, &relocated, sizeof relocated);
    }
    memcpy(code_map, private_code, sizeof private_code);
    DWORD old_protect;
    if (!VirtualProtect(code_map, 0x10000, PAGE_EXECUTE_READ, &old_protect) ||
        !FlushInstructionCache(GetCurrentProcess(), code_map, sizeof private_code)) {
        fprintf(stderr, "private code finalization failed: %lu\n",
                (unsigned long)GetLastError()); return 3;
    }
    memset(scratch, 0, 0x10000); /* one seed for each independent implementation sequence */
    Result results[80] = {{0}};
    for (unsigned int i = 0; i < 40; ++i) {
        Input *in = &guarded.inputs[i]; uint8_t mask = (uint8_t)in->initial_mask;
        set_fpu((uint16_t)in->control_word);
        nfs3_call_original(code_map, in->point, in->line, in->bounds, in->policy,
                           &mask, scratch, &results[i]);
    }
    /* Independent maintained-C run starts with the same one-time zero seed. */
    memset(gLineBoundaryCandidate_00791c08, 0, sizeof gLineBoundaryCandidate_00791c08);
    for (unsigned int i = 0; i < 40; ++i) {
        Input *in = &guarded.inputs[i]; uint8_t mask = (uint8_t)in->initial_mask;
        set_fpu((uint16_t)in->control_word);
        float *ret = Nfs3LineBoundaryCandidate_00485c30(in->point, in->line, in->bounds,
                                                        in->policy, &mask);
        record_c(&results[40 + i], ret, &mask);
        if (ret && ret != gLineBoundaryCandidate_00791c08) {
            fprintf(stderr, "maintained return is not shared result storage\n"); return 4;
        }
        results[40 + i].returned = ret ? 1u : 0u;
    }
    for (unsigned int i = 0; i < 4; ++i) {
        if (guarded.before[i] != 0xA5A5A5A5u || guarded.after[i] != 0xA5A5A5A5u) {
            fprintf(stderr, "input array canary changed\n"); return 4;
        }
    }
    if (memcmp(input_snapshot, guarded.inputs, sizeof input_snapshot) != 0) {
        fprintf(stderr, "input arrays changed\n"); return 4;
    }
    f = fopen(argv[3], "wb");
    if (!f) { perror(argv[3]); return 2; }
    uint32_t mapping_addresses[2] = {(uint32_t)(uintptr_t)code_map,
                                     (uint32_t)(uintptr_t)scratch};
    int ok = fwrite(mapping_addresses, sizeof mapping_addresses, 1, f) == 1 &&
             fwrite(results, sizeof(Result), 80, f) == 80 && fclose(f) == 0;
    return ok ? 0 : 2;
}
